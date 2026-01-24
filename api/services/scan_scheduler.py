import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
import threading
from typing import Dict, Any, Optional, List

from db.sqlite import get_all_wled_devices
from api.services.scheduler_status import SchedulerStatus
from services.settings_service import get_setting

logger = logging.getLogger(__name__)

class ScanScheduler:
    """
    Scheduler for periodic network scanning and device refresh.
    Runs network scan to discover new devices and refresh existing ones.
    """

    def __init__(self):
        self.is_running = False
        self.thread = None
        # Run every 7 days by default
        self.interval_days = 7
        self.status = SchedulerStatus(self.interval_days, "Network Scan Scheduler")
        self._task = None
        self.last_scan_results: Optional[Dict[str, Any]] = None
        self.scan_results_file = "database/last_scan_results.json"
    
    async def start(self):
        """Start the scan scheduler."""
        if self.is_running:
            logger.warning("Scan scheduler already running")
            return
        
        logger.info("Starting scan scheduler")
        self.is_running = True
        self.status.set_running()
        
        # Load last scan results if they exist
        self._load_scan_results()
        
        # Start the scheduler in a separate thread
        self.thread = threading.Thread(target=self._run_scheduler_thread)
        self.thread.daemon = True
        self.thread.start()
        
        logger.info(f"Scan scheduler started (runs every {self.interval_days} day(s))")
    
    def _run_scheduler_thread(self):
        """Run the scheduler loop in a thread."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self._scheduler_loop())
        except Exception as e:
            logger.error(f"Error in scan scheduler thread: {e}", exc_info=True)
        finally:
            loop.close()
    
    async def _scheduler_loop(self):
        """
        Main scheduler loop. Runs the scan process periodically.
        """
        first_run = True
        
        while self.is_running:
            try:
                # Run immediately on first execution, then follow the schedule
                if first_run:
                    # Wait a bit to let the system initialize fully
                    initial_delay = get_setting("scheduler_initial_delay") or 120
                    await asyncio.sleep(initial_delay)
                    first_run = False
                    logger.info("Running initial scheduled network scan")
                    await self.run_network_scan()
                
                # Wait for the next scheduled run
                # Get interval from settings (default 168 hours = 7 days)
                interval_hours = get_setting("network_scan_interval_hours") or 168
                self.interval_days = interval_hours / 24.0
                self.status.update_interval(self.interval_days)
                
                logger.info(f"Next scheduled network scan in {interval_hours} hours ({self.interval_days:.1f} days)")
                await asyncio.sleep(interval_hours * 60 * 60)
                logger.info("Running scheduled network scan")
                await self.run_network_scan()
            except Exception as e:
                logger.error(f"Error in scan scheduler loop: {e}", exc_info=True)
                self.status.update_error(str(e))
                # If there's an error, wait a bit and retry
                await asyncio.sleep(300)
    
    async def stop(self):
        """Stop the scan scheduler."""
        if not self.is_running:
            return
        
        logger.info("Stopping scan scheduler")
        self.is_running = False
        self.status.set_stopped()
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
            if self.thread.is_alive():
                logger.warning("Scan scheduler thread did not stop gracefully")
        
        logger.info("Scan scheduler stopped")
    
    def _load_scan_results(self):
        """Load last scan results from file."""
        try:
            if os.path.exists(self.scan_results_file):
                with open(self.scan_results_file, 'r') as f:
                    self.last_scan_results = json.load(f)
                logger.info(f"Loaded last scan results from {self.scan_results_file}")
        except Exception as e:
            logger.warning(f"Failed to load last scan results: {e}")
            self.last_scan_results = None
    
    def _save_scan_results(self, results: Dict[str, Any]):
        """Save scan results to file."""
        try:
            os.makedirs(os.path.dirname(self.scan_results_file), exist_ok=True)
            with open(self.scan_results_file, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Saved scan results to {self.scan_results_file}")
        except Exception as e:
            logger.error(f"Failed to save scan results: {e}")
    
    async def run_network_scan(self) -> bool:
        """
        Execute network scan to discover devices and refresh their information.
        Returns True if successful, False otherwise.
        """
        try:
            start_time = datetime.now()
            logger.info("Starting network scan")
            
            # Import here to avoid circular imports
            from scanner.wled_scan import scan_network, get_local_ip
            from api.services.scan_service import process_device
            import ipaddress
            
            # Get network range from settings or fallback to local network
            network_cidr = get_setting("network_range")
            if not network_cidr:
                local_ip = get_local_ip()
                # Assume /24 network
                network_cidr = str(ipaddress.IPv4Network(f"{local_ip}/24", strict=False))
            logger.info(f"Scanning network: {network_cidr}")
            
            # Perform network scan to find IPs with WLED devices
            found_ips = scan_network(network_cidr)
            logger.info(f"Found {len(found_ips)} potential WLED devices")
            
            # Track existing devices before scan
            existing_devices_before = get_all_wled_devices()
            existing_macs_before = {d.mac for d in existing_devices_before}
            
            # Process each discovered device using the standard process_device function
            # This ensures proper handling of configs, versions, backups, and health checks
            processed_devices = []
            for ip in found_ips:
                try:
                    logger.debug(f"Processing device at {ip}")
                    # process_device handles everything: device info retrieval, validation,
                    # DB updates, config versions, backups, and health checks
                    # Use None for timeout to let it fall back to configured info_timeout
                    result = await process_device(ip, existingMac=None, timeout=None)
                    if result:
                        processed_devices.append(result)
                        logger.debug(f"Successfully processed device at {ip}: MAC={result}")
                except Exception as e:
                    logger.error(f"Failed to process device at {ip}: {e}")
            
            logger.info(f"Successfully processed {len(processed_devices)} devices")
            
            # Calculate new vs updated devices
            existing_devices_after = get_all_wled_devices()
            existing_macs_after = {d.mac for d in existing_devices_after}
            
            new_devices = len(existing_macs_after - existing_macs_before)
            updated_devices = len(processed_devices) - new_devices
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            # Get device details for scan results (lightweight version)
            scanned_device_list = []
            for mac in processed_devices:
                device = next((d for d in existing_devices_after if d.mac == mac), None)
                if device:
                    scanned_device_list.append({
                        "mac": device.mac,
                        "ip": device.last_ip,
                        "name": device.name or device.local_name or device.hostname,
                        "status": device.status
                    })
            
            # Prepare scan results
            scan_results = {
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": duration,
                "total_discovered": len(processed_devices),
                "new_devices": new_devices,
                "updated_devices": updated_devices,
                "devices": scanned_device_list
            }
            
            # Save results
            self.last_scan_results = scan_results
            self._save_scan_results(scan_results)
            
            # Update status
            message = f"Scanned network: {len(processed_devices)} devices found ({new_devices} new, {updated_devices} updated) in {duration:.2f}s"
            self.status.update_success(message)
            logger.info(f"Network scan completed: {message}")
            
            return True
            
        except Exception as e:
            error_msg = f"Network scan failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.status.update_error(error_msg)
            return False
    
    async def run_now(self) -> bool:
        """Trigger an immediate network scan (for manual execution)."""
        logger.info("Manually triggered network scan")
        return await self.run_network_scan()
    
    def get_last_scan_results(self) -> Optional[Dict[str, Any]]:
        """Get the results from the last scan."""
        if not self.last_scan_results:
            self._load_scan_results()
        return self.last_scan_results


# Global instance
scan_scheduler = ScanScheduler()
