import os
import logging
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional

from db.sqlite import get_all_wled_devices
from api.services.base_scheduler import BaseScheduler

logger = logging.getLogger(__name__)

class DeviceRefreshScheduler(BaseScheduler):
    """
    Scheduler for periodic device refresh.
    Refreshes all devices by fetching their latest configuration, creating backups,
    version records, and updating health status.
    """

    def __init__(self):
        # Initialize base with default interval (1 day)
        super().__init__(interval_days=1)
        # Run interval in hours (24 hours = 1 day)
        self.interval_hours = 1

    def _get_scheduler_name(self) -> str:
        return "Device Refresh Scheduler"

    async def _do_work(self) -> bool:
        """Wrapper for refresh_all_devices to satisfy abstract method"""
        return await self.refresh_all_devices()
    
    async def _scheduler_loop(self):
        """
        Main scheduler loop. Refreshes all devices at the configured interval.
        The first refresh runs after startup.
        """
        first_run = True
        
        while self.is_running:
            try:
                # Run immediately on first execution, then follow the schedule
                if first_run:
                    # Wait a bit to let the system initialize fully
                    await asyncio.sleep(120)  # Wait 2 minutes after startup
                    first_run = False
                    logger.info("Running initial scheduled device refresh")
                    await self.refresh_all_devices()
                
                # Get interval from settings (default 1 hour)
                from services.settings_service import get_setting
                interval_hours = get_setting("device_refresh_interval_hours") or 1
                self.interval_hours = interval_hours
                # Update status interval (convert hours to days for compatibility)
                self.status.update_interval(self.interval_hours / 24.0)
                
                logger.info(f"Next scheduled device refresh in {self.interval_hours} hours")
                await asyncio.sleep(self.interval_hours * 60 * 60)
                logger.info("Running scheduled device refresh")
                await self.refresh_all_devices()
            except Exception as e:
                logger.error(f"Error in device refresh scheduler loop: {e}", exc_info=True)
                # If there's an error, wait a bit and retry
                await asyncio.sleep(300)

    async def refresh_all_devices(self):
        """
        Refresh all registered devices using the full process_device flow.
        This updates device info, creates backups and versions if changed, and checks health.
        """
        try:
            logger.info("Starting scheduled device refresh for all devices")
            
            # Import here to avoid circular imports
            from api.services.scan_service import process_device
            
            devices = get_all_wled_devices()
            success_count = 0
            failed_count = 0
            failed_devices = []
            
            for device in devices:
                try:
                    if device.last_ip:
                        logger.info(f"Refreshing device {device.name} ({device.last_ip})")
                        # Use process_device which handles:
                        # - Fetching latest config, info, state
                        # - Updating device record
                        # - Creating backups if config changed
                        # - Creating version records if config changed
                        # - Performing health check
                        result = await process_device(device.last_ip, device.mac, timeout=10.0)
                        if result:
                            success_count += 1
                            logger.debug(f"Successfully refreshed device {device.name}")
                        else:
                            failed_count += 1
                            failed_devices.append(device.name or device.mac)
                            logger.warning(f"Failed to refresh device {device.name} - process_device returned None")
                    else:
                        logger.warning(f"Skipping refresh for {device.name} - no IP address")
                except Exception as e:
                    device_name = device.name if device.name else f"Device at {device.last_ip or 'unknown IP'}"
                    logger.error(f"Failed to refresh {device_name}: {str(e)}")
                    failed_devices.append(device_name)
                    failed_count += 1
            
            result_msg = f"Completed device refresh: {success_count} successful, {failed_count} failed out of {len(devices)} devices"
            logger.info(result_msg)
            
            # Enhanced error reporting with device names
            if failed_count == 0:
                self.status.update_success(
                    result_msg, 
                    device_success=success_count, 
                    device_total=len(devices)
                )
            elif success_count > 0:
                # Partial success -> Warning
                warning_msg = f"{failed_count} devices failed: {', '.join(failed_devices)} - {result_msg}"
                self.status.update_warning(
                    warning_msg,
                    device_success=success_count,
                    device_total=len(devices)
                )
            else:
                error_msg = f"{failed_count} devices failed: {', '.join(failed_devices)} - {result_msg}"
                logger.warning(f"Failed refresh devices ({failed_count} out of {len(devices)}): {', '.join(failed_devices)}")
                self.status.update_error(error_msg)
            return True
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error in scheduled device refresh: {error_msg}", exc_info=True)
            self.status.update_error(error_msg)
            return False


# Global instance to be used by the server
device_refresh_scheduler = DeviceRefreshScheduler()
