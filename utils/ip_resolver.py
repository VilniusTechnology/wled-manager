"""
IP Resolution Utility for WLED devices.

Resolves device IP using multiple strategies when stored IP becomes stale:
1. ARP cache lookup (fastest)
2. Network scan with MAC match (most reliable)
3. mDNS resolution (fallback)
"""

import subprocess
import re
import socket
import logging
import ipaddress
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


def normalize_mac(mac: str) -> str:
    """Normalize MAC address to lowercase without separators."""
    if not mac:
        return ""
    return mac.lower().replace(':', '').replace('-', '')


def get_ip_from_arp_cache(mac: str) -> Optional[str]:
    """
    Look up IP address from system ARP cache by MAC address.
    Works on macOS and Linux.
    """
    if not mac:
        return None
    
    normalized_mac = normalize_mac(mac)
    
    try:
        # Works on both macOS and Linux
        result = subprocess.run(['arp', '-an'], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            logger.debug(f"ARP command failed with return code {result.returncode}")
            return None
        
        # Parse ARP output: "(192.168.0.100) at aa:bb:cc:dd:ee:ff ..."
        for line in result.stdout.split('\n'):
            # Extract IP and MAC from line
            ip_match = re.search(r'\((\d+\.\d+\.\d+\.\d+)\)', line)
            mac_match = re.search(
                r'([0-9a-f]{1,2}:[0-9a-f]{1,2}:[0-9a-f]{1,2}:[0-9a-f]{1,2}:[0-9a-f]{1,2}:[0-9a-f]{1,2})',
                line, 
                re.I
            )
            
            if ip_match and mac_match:
                arp_mac = normalize_mac(mac_match.group(1))
                if arp_mac == normalized_mac:
                    found_ip = ip_match.group(1)
                    logger.info(f"Found IP {found_ip} for MAC {mac} in ARP cache")
                    return found_ip
                    
    except subprocess.TimeoutExpired:
        logger.debug("ARP command timed out")
    except FileNotFoundError:
        logger.debug("ARP command not found on this system")
    except Exception as e:
        logger.debug(f"ARP lookup failed: {e}")
    
    return None


import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Cache for tracking when a MAC address scan last failed: {normalized_mac: timestamp}
_failed_scan_cache = {}
# Minimum interval between full network scans for the same unreachable MAC (12 hours)
SCAN_COOLDOWN_SECONDS = 43200

# Scan-specific requests session with NO retries (fail-fast on empty IPs)
_scan_session = None

def _get_scan_session():
    global _scan_session
    if _scan_session is None:
        session = requests.Session()
        adapter = HTTPAdapter(
            pool_connections=50,
            pool_maxsize=50,
            max_retries=Retry(total=0)
        )
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        _scan_session = session
    return _scan_session


def find_device_by_mac_scan(mac: str, network_cidr: str, timeout: float = 1.0) -> Optional[str]:
    """
    Scan network and find device by MAC address.
    Uses a fast fail-fast session without HTTP retries to prevent connection timeouts flooding logs.
    Includes a 12-hour cooldown per MAC to avoid continuous network sweeps for offline devices.
    """
    if not mac or not network_cidr:
        return None
    
    normalized_mac = normalize_mac(mac)
    
    # Check cooldown: if this MAC was scanned recently and not found, skip scanning
    now = time.time()
    last_failed = _failed_scan_cache.get(normalized_mac)
    if last_failed and (now - last_failed) < SCAN_COOLDOWN_SECONDS:
        remaining_min = int((SCAN_COOLDOWN_SECONDS - (now - last_failed)) / 60)
        logger.debug(f"Skipping network scan for MAC {mac}: cooldown active for another {remaining_min}m")
        return None
    
    try:
        ips = [str(ip) for ip in ipaddress.IPv4Network(network_cidr, strict=False)]
        logger.info(f"Scanning {len(ips)} IPs in {network_cidr} to locate MAC {mac}...")
        
        session = _get_scan_session()
        
        # Temporarily suppress urllib3 connection warnings during network sweep
        urllib_logger = logging.getLogger("urllib3.connectionpool")
        prev_level = urllib_logger.level
        urllib_logger.setLevel(logging.ERROR)
        
        def check_ip_for_mac(ip: str) -> Optional[str]:
            """Check if device at IP has the target MAC."""
            try:
                r = session.get(f"http://{ip}/json/info", timeout=timeout)
                if r.status_code == 200:
                    data = r.json()
                    device_mac = normalize_mac(data.get('mac', ''))
                    if device_mac == normalized_mac:
                        return ip
            except Exception:
                pass
            return None
        
        try:
            # Parallel scan with max 50 workers
            with ThreadPoolExecutor(max_workers=50) as executor:
                futures = {executor.submit(check_ip_for_mac, ip): ip for ip in ips}
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        logger.info(f"Found device MAC {mac} at {result} via network scan")
                        # Clear failure cache on success
                        _failed_scan_cache.pop(normalized_mac, None)
                        for f in futures:
                            f.cancel()
                        return result
        finally:
            urllib_logger.setLevel(prev_level)
                    
        # Device was not found in the entire subnet: record cooldown
        _failed_scan_cache[normalized_mac] = now
        logger.info(f"Network scan complete: MAC {mac} not found in {network_cidr}. Cooldown active for {SCAN_COOLDOWN_SECONDS // 3600}h.")
                    
    except Exception as e:
        logger.error(f"Network scan for MAC failed: {e}")
    
    return None


def resolve_mdns(hostname: str) -> Optional[str]:
    """
    Try to resolve mDNS hostname to IP address.
    Not available on all systems.
    """
    if not hostname:
        return None
    
    mdns_name = f"{hostname}.local" if not hostname.endswith('.local') else hostname
    
    try:
        ip = socket.gethostbyname(mdns_name)
        logger.info(f"Resolved mDNS {mdns_name} to {ip}")
        return ip
    except socket.gaierror as e:
        logger.debug(f"mDNS resolution failed for {mdns_name}: {e}")
    except Exception as e:
        logger.debug(f"mDNS resolution error: {e}")
    
    return None


def resolve_device_ip(
    mac: str, 
    hostname: str = None, 
    network_cidr: str = None,
    skip_arp: bool = False,
    skip_mdns: bool = False,
    skip_scan: bool = False
) -> Optional[str]:
    """
    Resolve device IP using multiple strategies in priority order.
    
    Args:
        mac: Device MAC address (required)
        hostname: Device mDNS hostname (optional)
        network_cidr: Network range for scanning, e.g., "192.168.0.0/24" (optional)
        skip_arp: Skip ARP cache lookup
        skip_mdns: Skip mDNS resolution
        skip_scan: Skip network scan
    
    Returns:
        Resolved IP address or None if all strategies fail
    
    Priority:
    1. ARP cache lookup (instant, no network traffic)
    2. mDNS resolution (fast, if available)
    3. Network scan with MAC match (slower, most reliable)
    """
    if not mac:
        logger.warning("Cannot resolve IP: no MAC address provided")
        return None
    
    # Strategy 1: ARP cache (fastest)
    if not skip_arp:
        ip = get_ip_from_arp_cache(mac)
        if ip:
            return ip
    
    # Strategy 2: mDNS (fast when available)
    if not skip_mdns and hostname:
        ip = resolve_mdns(hostname)
        if ip:
            return ip
    
    # Strategy 3: Network scan (slowest but most reliable)
    if not skip_scan and network_cidr:
        ip = find_device_by_mac_scan(mac, network_cidr)
        if ip:
            return ip
    
    logger.warning(f"Could not resolve IP for MAC {mac}")
    return None
