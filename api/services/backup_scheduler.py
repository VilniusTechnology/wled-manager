import os
import logging
import asyncio
from datetime import datetime, timedelta
import threading
from typing import List, Dict, Any, Optional
from zoneinfo import ZoneInfo

from db.sqlite import get_all_wled_devices, get_backups_for_device
from db.backup_models import WLEDBackupDBModel
from db.models import WLEDDevice
from scanner.wled_backup_retriever import WLEDBackupRetriever
from api.services.scheduler_status import SchedulerStatus
from api.services.backup_retention import parse_wled_timestamp, select_backups_for_deletion
from services.settings_service import get_setting

logger = logging.getLogger(__name__)

# Weekly wall-clock slot for the scheduled backup, in the configured app timezone.
# weekday follows datetime.weekday(): Monday=0 ... Sunday=6.
SCHEDULE_WEEKDAY = 1  # Tuesday
SCHEDULE_HOUR = 1
SCHEDULE_MINUTE = 30
DEFAULT_TIMEZONE = "Europe/Vilnius"
WEEK_SECONDS = 7 * 24 * 60 * 60

class BackupScheduler:
    """
    Scheduler for weekly backups and cleanup of old backups.
    Runs once a week and cleans up backups older than 6 months
    if at least one newer backup exists for the device.

    The run is anchored to a wall-clock slot (Tuesday 01:30 in the configured
    timezone) instead of a fixed offset from process start, so pod restarts no
    longer shift the schedule or trigger an unsolicited backup + email.
    """

    def __init__(self):
        self.is_running = False
        self.thread = None
        self.backup_retriever = WLEDBackupRetriever()
        # Kept for status display / fallback only; the loop uses the weekly slot
        self.interval_hours = get_setting("backup_interval_hours") or 168
        # Retention count: 10 (default, overridden by settings)
        self.retention_count = get_setting("backup_retention_count") or 10
        self.status = SchedulerStatus(7.0, "Backup Scheduler")

    def _timezone(self) -> ZoneInfo:
        """Timezone used to evaluate the weekly slot."""
        tz_name = get_setting("timezone") or DEFAULT_TIMEZONE
        try:
            return ZoneInfo(tz_name)
        except Exception:
            logger.warning(f"Invalid timezone '{tz_name}', falling back to {DEFAULT_TIMEZONE}")
            return ZoneInfo(DEFAULT_TIMEZONE)

    def next_run_at(self, now: Optional[datetime] = None) -> datetime:
        """Return the next weekly run time (timezone aware)."""
        tz = self._timezone()
        now = now or datetime.now(tz)
        if now.tzinfo is None:
            now = now.replace(tzinfo=tz)
        candidate = now.replace(
            hour=SCHEDULE_HOUR, minute=SCHEDULE_MINUTE, second=0, microsecond=0
        )
        candidate += timedelta(days=(SCHEDULE_WEEKDAY - now.weekday()) % 7)
        if candidate <= now:
            candidate += timedelta(days=7)
        return candidate

    async def _wait_until(self, target: datetime):
        """Sleep until target, waking up regularly so stop() stays responsive."""
        tz = self._timezone()
        while self.is_running:
            remaining = (target - datetime.now(tz)).total_seconds()
            if remaining <= 0:
                return
            await asyncio.sleep(min(remaining, 60))
    
    async def start(self):
        """Start the backup scheduler in a separate thread."""
        if self.is_running:
            logger.warning("Backup scheduler already running")
            return
        
        logger.info("Starting backup scheduler")
        self.is_running = True
        self.status.set_running()
        
        # Start the scheduler in a separate thread
        self.thread = threading.Thread(target=self._run_scheduler_thread)
        self.thread.daemon = True
        self.thread.start()
        
        next_run = self.next_run_at()
        logger.info(f"Backup scheduler started (weekly slot: {next_run.isoformat()})")
    
    def _run_scheduler_thread(self):
        """Run the scheduler loop in a thread."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self._scheduler_loop())
        except Exception as e:
            logger.error(f"Error in backup scheduler thread: {e}", exc_info=True)
        finally:
            loop.close()
    
    async def _scheduler_loop(self):
        """
        Main scheduler loop. Waits for the weekly wall-clock slot, runs the
        backup, then waits for the next slot. Nothing runs on startup.
        """
        while self.is_running:
            try:
                # Refresh settings in case they changed
                self.retention_count = get_setting("backup_retention_count") or 10
                self.status.update_interval(7.0)

                next_run = self.next_run_at()
                self.status.next_run = next_run
                logger.info(f"Next scheduled backup: {next_run.isoformat()}")

                await self._wait_until(next_run)
                if not self.is_running:
                    break

                logger.info("Running scheduled backup")
                await self.run_backup_and_cleanup()

                # Re-anchor on the wall clock (update_success uses now + interval)
                next_run = self.next_run_at()
                self.status.next_run = next_run
                logger.info(f"Next scheduled backup: {next_run.isoformat()}")

                # Avoid a second run inside the same slot
                await asyncio.sleep(60)
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}", exc_info=True)
                # If there's an error, wait a bit and retry
                await asyncio.sleep(300)
    
    async def stop(self):
        """Stop the backup scheduler."""
        if not self.is_running:
            return
        
        logger.info("Stopping backup scheduler")
        self.is_running = False
        self.status.set_stopped()
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
            if self.thread.is_alive():
                logger.warning("Backup scheduler thread did not terminate gracefully")
        
        logger.info("Backup scheduler stopped")
    
    async def run_now(self):
        """Manually trigger immediate execution of backup and cleanup."""
        return await self.run_backup_and_cleanup()

    async def run_backup_and_cleanup(self):
        """Run backup for all devices and cleanup old backups."""
        try:
            logger.info("Starting scheduled backup for all devices")
            success_count, failed_count = await self._create_backups_for_all_devices()
            logger.info("Starting cleanup of old backups")
            cleanup_count = await self._cleanup_old_backups()
            
            result_msg = f"Backup completed: {success_count} successful, {failed_count} failed. Cleaned up {cleanup_count} old backups."
            logger.info(result_msg)
            
            # Send backup email
            raw_email_setting = get_setting("backup_email_enabled")
            
            # Robust boolean check
            email_enabled = False
            if isinstance(raw_email_setting, bool):
                email_enabled = raw_email_setting
            elif isinstance(raw_email_setting, str):
                email_enabled = raw_email_setting.lower() in ('true', '1', 'yes', 'on')
            
            logger.info(f"Backup email setting: {raw_email_setting} (Effective: {email_enabled})")

            if email_enabled:
                try:
                    from api.services.email_service import EmailService
                    email_service = EmailService()
                    email_success, email_error = email_service.send_backup_email()
                    if email_success:
                        logger.info("Backup notification email sent successfully")
                    else:
                        logger.error(f"Failed to send backup notification email: {email_error}")
                except Exception as e:
                    logger.error(f"Error sending backup notification email: {e}")
            else:
                logger.info("Backup email notification disabled")

            if failed_count == 0:
                self.status.update_success(result_msg)
            else:
                self.status.update_error(f"{failed_count} backup failures: {result_msg}")
            return True
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error in scheduled backup: {error_msg}", exc_info=True)
            self.status.update_error(error_msg)
            return False
    
    async def _create_backups_for_all_devices(self):
        """Create backups for all registered devices."""
        devices = get_all_wled_devices()
        success_count = 0
        failed_count = 0
        failed_devices = []
        
        for device in devices:
            try:
                if device.last_ip:
                    logger.info(f"Creating backup for device {device.name} ({device.last_ip})")
                    self.backup_retriever.backup_device(device.last_ip)
                    success_count += 1
                else:
                    logger.warning(f"Skipping backup for {device.name} - no IP address")
            except Exception as e:
                device_name = device.name if device.name else f"Device at {device.last_ip or 'unknown IP'}"
                logger.error(f"Failed to backup {device_name}: {str(e)}")
                failed_devices.append(device_name)
                failed_count += 1
        
        # Enhanced logging with failed device names
        logger.info(f"Completed backups: {success_count} successful, {failed_count} failed out of {len(devices)} devices")
        if failed_devices:
            logger.warning(f"Failed backup devices ({failed_count} out of {len(devices)}): {', '.join(failed_devices)}")
        
        return success_count, failed_count
    
    async def _cleanup_old_backups(self):
        """Clean up backups using the GFS (grandfather-father-son) retention policy."""
        devices = get_all_wled_devices()
        total_cleaned = 0
        now = datetime.utcnow()

        for device in devices:
            try:
                if not device.mac:
                    continue

                # Get all backups for this device
                device_backups = get_backups_for_device(device.mac)
                if not device_backups:
                    continue

                backups_to_delete = select_backups_for_deletion(
                    device_backups,
                    timestamp=lambda b: parse_wled_timestamp(b.timestamp),
                    now=now,
                )

                if not backups_to_delete:
                    continue

                # Delete old backups
                for backup in backups_to_delete:
                    try:
                        # Delete physical files
                        self._delete_backup_files(backup)

                        # Delete database record
                        from db.sqlite import delete_backup
                        delete_backup(backup.id)

                        logger.info(f"Deleted excess backup {backup.id} for {device.name} from {backup.timestamp}")
                    except Exception as e:
                        logger.error(f"Failed to delete backup {backup.id}: {str(e)}")

                cleaned_count = len(backups_to_delete)
                total_cleaned += cleaned_count
                if cleaned_count > 0:
                    logger.info(f"Cleaned up {cleaned_count} old backups for {device.name}")

            except Exception as e:
                logger.error(f"Error cleaning up backups for device {device.name}: {str(e)}")

        return total_cleaned
    
    def _delete_backup_files(self, backup: WLEDBackupDBModel):
        """Delete the physical backup files."""
        try:
            if backup.presets_path and os.path.exists(backup.presets_path):
                os.remove(backup.presets_path)
        except Exception as e:
            logger.error(f"Error deleting presets file {backup.presets_path}: {str(e)}")
        
        try:
            if backup.cfg_path and os.path.exists(backup.cfg_path):
                os.remove(backup.cfg_path)
        except Exception as e:
            logger.error(f"Error deleting config file {backup.cfg_path}: {str(e)}")

# Global instance to be used by the server
backup_scheduler = BackupScheduler()