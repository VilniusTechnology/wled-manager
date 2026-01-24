import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)

class SchedulerState(Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    ERROR = "error"
    WARNING = "warning"

class SchedulerStatus:
    """
    Tracks the status of a scheduler including last run time, 
    next scheduled run, current state, and any errors.
    """
    
    def __init__(self, interval_days: int, name: str = ""):
        self.name = name
        self.interval_days = interval_days
        self.last_run: Optional[datetime] = None
        self.last_success: Optional[datetime] = None
        self.next_run: Optional[datetime] = None
        self.current_state: SchedulerState = SchedulerState.STOPPED
        self.last_error: Optional[str] = None
        self.last_error_time: Optional[datetime] = None
        self.run_count = 0
        self.success_count = 0
        self.error_count = 0
        # Optional device-level metrics (for schedulers that check devices)
        self.device_success_count: Optional[int] = None
        self.device_total_count: Optional[int] = None
        
    def update_interval(self, interval_days: int):
        """Update the scheduler interval."""
        self.interval_days = interval_days
    
    def update_success(self, message: str = "", device_success: Optional[int] = None, device_total: Optional[int] = None):
        """Update status after successful run.

        Args:
            message: Optional message describing the run
            device_success: Optional count of successfully checked devices
            device_total: Optional total count of devices checked
        """
        now = datetime.now(timezone.utc)
        self.last_run = now
        self.last_success = now
        self.run_count += 1
        self.success_count += 1
        self.next_run = now + timedelta(days=self.interval_days)
        self.last_error = None  # Clear any previous error
        
        # Reset state to RUNNING (resolves ERROR/WARNING state)
        if self.current_state != SchedulerState.STOPPED:
             self.current_state = SchedulerState.RUNNING

        # Update device-level metrics if provided
        if device_success is not None and device_total is not None:
            self.device_success_count = device_success
            self.device_total_count = device_total

        logger.info(f"Scheduler {self.name} completed successfully: {message}")
    
    
    def update_warning(self, warning_message: str, device_success: Optional[int] = None, device_total: Optional[int] = None):
        """Update status after run with warnings (partial success)."""
        now = datetime.now(timezone.utc)
        self.last_run = now
        # We update last_success because it was partially successful
        self.last_success = now 
        
        self.last_error = warning_message 
        self.run_count += 1
        self.success_count += 1
        
        self.current_state = SchedulerState.WARNING
        self.next_run = now + timedelta(days=self.interval_days)
        
        # Update device-level metrics
        if device_success is not None and device_total is not None:
            self.device_success_count = device_success
            self.device_total_count = device_total
            
        logger.warning(f"Scheduler {self.name} completed with warning: {warning_message}")

    def update_error(self, error_message: str):
        """Update status after failed run."""
        now = datetime.now(timezone.utc)
        self.last_run = now
        self.last_error = error_message
        self.last_error_time = now
        self.run_count += 1
        self.error_count += 1
        self.current_state = SchedulerState.ERROR
        # Still schedule next run even after error
        self.next_run = now + timedelta(days=self.interval_days)
        logger.error(f"Scheduler {self.name} failed: {error_message}")
    
    def set_running(self):
        """Set scheduler state to running."""
        self.current_state = SchedulerState.RUNNING
        logger.info(f"Scheduler {self.name} started")
    
    def set_stopped(self):
        """Set scheduler state to stopped."""
        self.current_state = SchedulerState.STOPPED
        self.next_run = None
        logger.info(f"Scheduler {self.name} stopped")
    
    def get_status_dict(self) -> Dict[str, Any]:
        """Get status as dictionary for API responses."""
        status = {
            "name": self.name,
            "state": self.current_state.value,
            "interval_days": self.interval_days,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "last_success": self.last_success.isoformat() if self.last_success else None,
            "next_run": self.next_run.isoformat() if self.next_run else None,
            "last_error": self.last_error,
            "last_error_time": self.last_error_time.isoformat() if self.last_error_time else None,
            "run_count": self.run_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": (self.success_count / self.run_count * 100) if self.run_count > 0 else 0
        }

        # Add device-level metrics if available
        if self.device_success_count is not None and self.device_total_count is not None:
            status["device_success_count"] = self.device_success_count
            status["device_total_count"] = self.device_total_count
            status["device_success_rate"] = (self.device_success_count / self.device_total_count * 100) if self.device_total_count > 0 else 0

        return status
    
    def is_overdue(self, threshold_minutes: int = 60) -> bool:
        """Check if scheduler is overdue (next_run passed by more than threshold)."""
        if not self.next_run:
            return False
        return datetime.now(timezone.utc) > (self.next_run + timedelta(minutes=threshold_minutes))