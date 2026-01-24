import socket
import ipaddress
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import sys
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import required classes for full info flow
from .wled_retriever import WLEDRetriever
from .dto.wled_dto import WLEDDeviceFullInfoDTO
from .wled_json_builder import WLEDJsonBuilder
from services.settings_service import get_setting

logger = logging.getLogger(__name__)

# Thread-local session storage for connection pooling
_thread_local = threading.local()

def get_session():
    """Get or create a thread-local requests session with connection pooling."""
    if not hasattr(_thread_local, "session"):
        session = requests.Session()
        # Configure connection pooling
        pool_size = get_setting("connection_pool_size") or 20
        max_retries = get_setting("max_retries") or 1
        adapter = HTTPAdapter(
            pool_connections=pool_size,
            pool_maxsize=pool_size,
            max_retries=Retry(total=max_retries, backoff_factor=0.1)
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        _thread_local.session = session
    return _thread_local.session

def retrieve_wled_full_info(ip, timeout=None):
    """
    Retrieves complete information from a WLED device including its configuration, state, and info.
    
    Args:
        ip (str): IP address of the WLED device
        timeout (float, optional): Request timeout in seconds. Defaults to value from settings.
        
    Returns:
        dict: A dictionary containing device information with structure:
        {
            "mac": str,             # Device MAC address
            "ip": str,              # Device IP address
            "mqtt": dict,           # MQTT configuration
            "network": dict,        # Network configuration
            "cfg_full": dict,       # Complete device configuration
            "info_full": dict,      # Complete device information
            "state_full": dict,     # Current device state
            "has_static_ip": bool,  # Whether device uses static IP
            "discovery_date_time": str  # ISO datetime string or null
        }
    """
    logger.debug(f"Retrieving WLED device info from {ip} with timeout: {timeout}")
    if timeout is None:
        timeout = get_setting("info_timeout")
    try:
        extractor = WLEDRetriever(ip, timeout)
        # Get info first as it's the most basic request
        info = extractor.get_info()
        if not info:
            raise Exception("Failed to get device info")
            
        # Only proceed with state if info was successful
        # Small delay to prevent overwhelming the device
        time.sleep(0.1)
        state = extractor.get_state()
        time.sleep(0.1)
        cfg = extractor.get_cfg()
        if not state:
            raise Exception("Failed to get device state")
        if not cfg:
            raise Exception("Failed to get device config")
            
        mac = info.get("mac", "")
        ip_addr = info.get("ip", ip)
        dto = WLEDDeviceFullInfoDTO(
            mac=mac,
            ip=ip_addr,
            cfg_full=cfg,
            info_full=info,
            state_full=state
        )
        result = WLEDJsonBuilder.build(dto)
        
        # Add discovery_date_time from database if device exists
        if mac:
            # Import here to avoid circular imports
            from db.sqlite import get_wled_device
            existing_device = get_wled_device(mac)
            if existing_device and existing_device.created:
                result["discovery_date_time"] = existing_device.created.isoformat()
            else:
                result["discovery_date_time"] = None
        else:
            result["discovery_date_time"] = None
            
        return result
    except Exception as e:
        return {"ip": ip, "error": str(e)}

def get_local_ip():
    """Get the local IP address of the interface that would be used for internet connectivity."""
    try:
        # Try to get the IP that would be used to connect to a public IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))  # Google DNS
        IP = s.getsockname()[0]
        s.close()
        return IP
    except Exception:
        # Fallback: try to find an IP in common private network ranges
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Try connecting to a local network IP
            s.connect(('192.168.0.1', 80))
            IP = s.getsockname()[0]
            s.close()
            return IP
        except Exception:
            # Last resort: return 192.168.0.1 as a default
            return '192.168.0.1'

def scan_network_check_ip(ip, timeout):
    """Helper function to check a single IP using connection pooling."""
    # Create a new session for each check to avoid thread-local state issues
    with requests.Session() as session:
        # Configure connection pooling
        pool_size = 1
        max_retries = get_setting("max_retries") or 1
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=0.1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(
            pool_connections=pool_size,
            pool_maxsize=pool_size,
            max_retries=retry_strategy
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # logger.debug(f"Checking IP: {ip}, timeout: {timeout}")
        try:
            # Make HTTP request only
            url = f"http://{ip}/json/info"
            r = session.get(url, timeout=timeout, allow_redirects=True)
            if r.status_code == 200:
                data = r.json()
                # Check if it's a WLED device by looking for WLED-specific fields
                if 'ver' in data and 'name' in data:
                    logger.info(f"FOUND WLED device at {ip}")
                    return ip
                else:
                    logger.debug(f"IP {ip} responded but missing WLED fields: {data.keys()}")
            else:
                pass
                # logger.debug(f"IP {ip} returned status {r.status_code}")
        except requests.exceptions.ConnectTimeout:
            pass
        except requests.exceptions.ConnectionError:
            pass
        except requests.exceptions.ReadTimeout:
            pass
        except Exception as e:
            logger.error(f"Unexpected error checking {ip}: {type(e).__name__}: {e}")
    return None

def scan_network(network_cidr, timeout=None):
    logger.debug(f"Starting network scan on {network_cidr} with timeout {timeout}")
    
    if timeout is None:
        timeout = get_setting("scan_timeout") or 2.0
        
    ips = [str(ip) for ip in ipaddress.IPv4Network(network_cidr, strict=False)]
    found = []
    
    max_workers = get_setting("max_workers") or 50
    logger.debug(f"Scanning {len(ips)} IPs with {max_workers} workers")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(scan_network_check_ip, ip, timeout): ip for ip in ips}
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                found.append(result)

    logger.debug(f"Finished scanning network {network_cidr}, found devices: {found}")
    return found
