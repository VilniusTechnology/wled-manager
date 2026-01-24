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


def find_device_by_mac_scan(mac: str, network_cidr: str, timeout: float = 2.0) -> Optional[str]:
    """
    Scan network and find device by MAC address.
    Uses the existing WLED scan infrastructure.
    """
    if not mac or not network_cidr:
        return None
    
    normalized_mac = normalize_mac(mac)
    
    try:
        # Import here to avoid circular imports
        from scanner.wled_scan import get_session
        
        ips = [str(ip) for ip in ipaddress.IPv4Network(network_cidr, strict=False)]
        logger.debug(f"Scanning {len(ips)} IPs to find MAC {mac}")
        
        def check_ip_for_mac(ip: str) -> Optional[str]:
            """Check if device at IP has the target MAC."""
            try:
                session = get_session()
                r = session.get(f"http://{ip}/json/info", timeout=timeout)
                if r.status_code == 200:
                    data = r.json()
                    device_mac = normalize_mac(data.get('mac', ''))
                    if device_mac == normalized_mac:
                        return ip
            except Exception:
                pass
            return None
        
        # Parallel scan with max 50 workers
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = {executor.submit(check_ip_for_mac, ip): ip for ip in ips}
            for future in as_completed(futures):
                result = future.result()
                if result:
                    logger.info(f"Found device MAC {mac} at {result} via network scan")
                    # Cancel remaining futures
                    for f in futures:
                        f.cancel()
                    return result
                    
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
