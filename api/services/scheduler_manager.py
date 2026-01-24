import logging
from typing import Dict, List, Any
from api.services.device_refresh_scheduler import device_refresh_scheduler
from api.services.backup_scheduler import backup_scheduler
from api.services.health_check_scheduler import health_check_scheduler

from api.services.scan_scheduler import scan_scheduler
from services.settings_service import get_setting

logger = logging.getLogger(__name__)

class SchedulerManager:
    """
    Central manager for all periodic schedulers in the application.
    Provides unified interface for monitoring and controlling schedulers.
    """
    
    def __init__(self):
        # Registry of all schedulers
        self.schedulers = {
            "health_check": health_check_scheduler,
            "network_scan": scan_scheduler,
            "device_refresh": device_refresh_scheduler,
            "backup": backup_scheduler,
        }
    
    def get_scheduler_status(self, scheduler_name: str) -> Dict[str, Any]:
        """Get status of a specific scheduler."""
        scheduler = self.schedulers.get(scheduler_name)
        if not scheduler:
            raise ValueError(f"Unknown scheduler: {scheduler_name}")
        
        return scheduler.status.get_status_dict()
    
    def get_all_scheduler_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all schedulers."""
        statuses = {}
        for name, scheduler in self.schedulers.items():
            status_dict = scheduler.status.get_status_dict()
            status_dict['scheduler_id'] = name
            # Add friendly name if not already set
            if not status_dict.get('friendly_name'):
                status_dict['friendly_name'] = self._get_friendly_name(name)
            statuses[name] = status_dict
        return statuses
    
    def _get_friendly_name(self, scheduler_name: str) -> str:
        """Get a user-friendly name for a scheduler."""
        friendly_names = {
            "health_check": "Device Health Check",
            "network_scan": "Network Scan",
            "device_refresh": "Device Refresh",
            "backup": "Device Backup"
        }
        return friendly_names.get(scheduler_name, scheduler_name.replace('_', ' ').title())
    
    async def start_scheduler(self, scheduler_name: str) -> bool:
        """Start a specific scheduler."""
        scheduler = self.schedulers.get(scheduler_name)
        if not scheduler:
            raise ValueError(f"Unknown scheduler: {scheduler_name}")
        
        # Check if scheduler is disabled via settings
        if get_setting(f"disable_{scheduler_name}"):
            logger.info(f"Scheduler {scheduler_name} is disabled in settings, skipping start")
            raise ValueError(f"Scheduler {scheduler_name} is disabled. Please enable auto-run first.")
        
        try:
            await scheduler.start()
            return True
        except Exception as e:
            logger.error(f"Failed to start scheduler {scheduler_name}: {e}")
            return False
    
    async def stop_scheduler(self, scheduler_name: str) -> bool:
        """Stop a specific scheduler."""
        scheduler = self.schedulers.get(scheduler_name)
        if not scheduler:
            raise ValueError(f"Unknown scheduler: {scheduler_name}")
        
        try:
            await scheduler.stop()
            return True
        except Exception as e:
            logger.error(f"Failed to stop scheduler {scheduler_name}: {e}")
            return False
    
    async def run_scheduler_now(self, scheduler_name: str) -> bool:
        """Trigger immediate execution of a scheduler."""
        scheduler = self.schedulers.get(scheduler_name)
        if not scheduler:
            raise ValueError(f"Unknown scheduler: {scheduler_name}")
        
        try:
            logger.info(f"Manually triggering scheduler: {scheduler_name}")
            
            # Try to use the generic run_now method first
            if hasattr(scheduler, 'run_now'):
                result = await scheduler.run_now()
            elif scheduler_name == "health_check":
                result = await scheduler.run_health_check()
            elif scheduler_name == "network_scan":
                result = await scheduler.run_network_scan()
            elif scheduler_name == "device_refresh":
                result = await scheduler.refresh_all_devices()
            elif scheduler_name == "backup":
                result = await scheduler.run_backup_and_cleanup()
            else:
                logger.warning(f"Manual run not implemented for scheduler: {scheduler_name}")
                return False
            
            return result
        except Exception as e:
            logger.error(f"Failed to run scheduler {scheduler_name} manually: {e}")
            scheduler.status.update_error(f"Manual run failed: {str(e)}")
            return False
    
    async def start_all_schedulers(self) -> Dict[str, bool]:
        """Start all schedulers."""
        results = {}
        for name in self.schedulers.keys():
            results[name] = await self.start_scheduler(name)
        return results
    
    async def stop_all_schedulers(self) -> Dict[str, bool]:
        """Stop all schedulers."""
        results = {}
        for name in self.schedulers.keys():
            results[name] = await self.stop_scheduler(name)
        return results
    
    def get_scheduler_names(self) -> List[str]:
        """Get list of all scheduler names."""
        return list(self.schedulers.keys())

# Global instance to be used by the API
scheduler_manager = SchedulerManager()