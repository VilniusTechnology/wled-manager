import logging
import asyncio
from datetime import datetime, timezone
import threading
from typing import Dict, Any

from db.sqlite import get_all_wled_devices
from api.services.base_scheduler import BaseScheduler
from services.settings_service import get_setting

logger = logging.getLogger(__name__)

class HealthCheckScheduler(BaseScheduler):
    """
    Scheduler for periodic device health checks.
    Runs every 30 seconds to check device connectivity and update status.
    """

    def __init__(self):
        # Initialize base with default interval (minimal 0 initially)
        super().__init__(interval_days=0)
        # Run every 30 seconds
        self.interval_seconds = 30
        self.status.update_interval(self.interval_seconds / (24 * 60 * 60))

    def _get_scheduler_name(self) -> str:
        return "Health Check Scheduler"

    async def _do_work(self) -> bool:
        """Wrapper for run_health_check to satisfy abstract method"""
        return await self.run_health_check()
    
    # Override start to use create_task instead of thread if desired?
    # Original implementation used a task in the EVENT LOOP if it was already running, 
    # but BaseScheduler uses a separate thread.
    # To keep behavioral consistency with other schedulers and simplify, we will use the BaseScheduler's thread approach.
    # The original implementation had `self._task = asyncio.create_task(self._scheduler_loop())` which implies it ran on the main loop?
    # Actually `health_check_scheduler` was imported and started by `scheduler_manager`.
    # `scheduler_manager` calls `start()`.
    # Let's stick to BaseScheduler's thread model which is safer for blocking ops (though health check should be async).
    # Since `BaseScheduler` starts a thread with new loop, `_scheduler_loop` runs in that thread.
    
    async def _scheduler_loop(self):
        """Main scheduler loop. Checks device health every 30 seconds."""
        while self.is_running:
            try:
                # Update interval from settings first
                interval_seconds = get_setting("health_check_interval_seconds") or 60
                self.interval_seconds = int(interval_seconds)
                
                # Update status interval info
                self.status.update_interval(self.interval_seconds / (24 * 60 * 60))

                # Check if cleanup is disabled? Settings service doesn't have disable_health_check usually but let's check.
                if not get_setting("disable_health_check"):
                     await self.run_health_check()
                else:
                     self.status.set_stopped()
                     logger.debug("Health check disabled, skipping")

            except Exception as e:
                logger.error(f"Error in health check scheduler loop: {e}", exc_info=True)
                self.status.update_error(str(e))
            
            # Wait for the next scheduled run
            await asyncio.sleep(self.interval_seconds)
    
    async def stop(self):
        """Stop the health check scheduler."""
        # Override to ensure we set stop flag properly and wait
        await super().stop()
        
    async def run_health_check(self) -> bool:
        """
        Execute health check for all devices.
        Returns True if successful, False otherwise.
        """
        try:
            start_time = datetime.now(timezone.utc)
            logger.debug("Starting health check run")
            
            # Import here to avoid circular imports
            # Import from device_service instead of controller to avoid circular imports and bad practice
            from api.services.device_service import check_and_update_device_status
            
            devices = get_all_wled_devices()
            # Only check devices with an IP address
            devices_to_check = [d for d in devices if d.last_ip]
            ips = [d.last_ip for d in devices_to_check]
            
            if not devices_to_check:
                logger.debug("No device IPs to check")
                self.status.update_success("No devices to check", device_success=0, device_total=0)
                return True
            
            logger.debug(f"Health checking {len(devices_to_check)} devices")
            # Pass both IP and MAC to the check function, plus hostname for mDNS fallback
            tasks = [check_and_update_device_status(d.last_ip, d.mac, d.hostname) for d in devices_to_check]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Separate successful and failed results
            successful_checks = []
            failed_checks = []
            failed_devices = []
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    failed_checks.append(result)
                    failed_devices.append(ips[i])
                elif hasattr(result, 'status') and result.status == 'dead':
                    failed_checks.append(f"Device dead: {result.status}")
                    failed_devices.append(ips[i])
                else:
                    successful_checks.append(result)
                    # Add detailed logging for online status decision
                    if hasattr(result, 'status') and result.status == 'online':
                         logger.debug(f"Device {ips[i]} confirmed ONLINE via HTTP check")
                    elif hasattr(result, 'status') and result.status == 'good':
                         logger.debug(f"Device {ips[i]} confirmed GOOD via HTTP check")
                    else:
                         # Likely a dict result
                         logger.debug(f"Device {ips[i]} check result: {result}")
            
            # Calculate duration
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            # Update status with device-level metrics
            message = f"Checked {len(ips)} devices: {len(successful_checks)} ok, {len(failed_checks)} failed in {duration:.2f}s"

            if failed_checks:
                # Get device names for failed IPs
                failed_device_info = []
                for ip in failed_devices:
                    device = next((d for d in devices if d.last_ip == ip), None)
                    device_name = device.name if device and device.name else f"Device at {ip}"
                    failed_device_info.append(f"{device_name} ({ip})")

                logger.warning(f"Failed devices ({len(failed_checks)} out of {len(devices)}): {', '.join(failed_device_info)}")

            # Pass device-level metrics to status
            self.status.update_success(message, device_success=len(successful_checks), device_total=len(ips))
            logger.debug(f"Health check completed: {message}")
            
            return True
            
        except Exception as e:
            error_msg = f"Health check failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.status.update_error(error_msg)
            return False


# Global instance
health_check_scheduler = HealthCheckScheduler()
