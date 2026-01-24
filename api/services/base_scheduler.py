import logging
import asyncio
import threading
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from api.services.scheduler_status import SchedulerStatus

logger = logging.getLogger(__name__)

class BaseScheduler(ABC):
    """
    Abstract base class for all schedulers.
    Handles lifecycle management (start/stop), threading, and status updates.
    """

    def __init__(self, interval_days: float = 0):
        self.is_running = False
        self.thread: Optional[threading.Thread] = None
        self.status = SchedulerStatus(interval_days, self._get_scheduler_name())
        self.interval_seconds = 0 # Can be used by subclasses that need second precision

    @abstractmethod
    def _get_scheduler_name(self) -> str:
        """Get the friendly name of the scheduler for logging and status."""
        pass

    @abstractmethod
    async def _do_work(self) -> bool:
        """
        Perform the actual scheduled work.
        Returns:
            bool: True if successful (or partial success), False on failure.
        """
        pass

    async def start(self):
        """Start the scheduler in a separate thread."""
        if self.is_running:
            logger.warning(f"{self._get_scheduler_name()} already running")
            return
        
        logger.info(f"Starting {self._get_scheduler_name()}")
        self.is_running = True
        self.status.set_running()
        
        # Start the scheduler in a separate thread
        self.thread = threading.Thread(target=self._run_scheduler_thread)
        self.thread.daemon = True
        self.thread.start()
        
        logger.info(f"{self._get_scheduler_name()} started")
    
    def _run_scheduler_thread(self):
        """Run the scheduler loop in a thread."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self._scheduler_loop())
        except Exception as e:
            logger.error(f"Error in {self._get_scheduler_name()} thread: {e}", exc_info=True)
        finally:
            loop.close()
    
    async def stop(self):
        """Stop the scheduler."""
        if not self.is_running:
            return
        
        logger.info(f"Stopping {self._get_scheduler_name()}")
        self.is_running = False
        self.status.set_stopped()
        
        if self.thread and self.thread.is_alive():
            # In a real async shutdown we might want to signal the loop to stop
            # But here we just rely on the flag self.is_running
            self.thread.join(timeout=5)
            if self.thread.is_alive():
                logger.warning(f"{self._get_scheduler_name()} thread did not terminate gracefully")
        
        logger.info(f"{self._get_scheduler_name()} stopped")
    
    async def run_now(self):
        """Manually trigger immediate execution."""
        return await self._do_work()

    async def _scheduler_loop(self):
        """
        Main scheduler loop.
        Subclasses should typically invoke _do_work based on their interval.
        Since intervals and logic vary (weekly vs daily vs seconds), 
        default implementation just calls a hook.
        
        However, since logic is quite different (some sleep days, some minutes),
        we'll keep this abstract or overridable.
        For DRY, we can implement a common loop if they all folow 'sleep X then work'.
        """
        pass
