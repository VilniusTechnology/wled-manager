"""
Utility functions for WLED device configuration analysis.
"""
from typing import Dict, Any, Optional

def detect_static_ip_config(config: Dict[str, Any]) -> bool:
    """
    Detect if a WLED device has a static IP configuration based on its config data.
    
    Args:
        config: The WLED device configuration dictionary
        
    Returns:
        bool: True if device has static IP configuration, False otherwise
    """
    # Check if network configuration exists
    nw_config = config.get('nw')
    if not nw_config or not isinstance(nw_config, dict):
        return False
    
    # Check network interfaces
    interfaces = nw_config.get('ins')
    if not interfaces or not isinstance(interfaces, list) or len(interfaces) == 0:
        return False
    
    # Check the first interface (primary network interface)
    primary_interface = interfaces[0]
    if not isinstance(primary_interface, dict):
        return False
    
    # A static IP configuration typically has:
    # - ip: static IP address (array of 4 integers)
    # - gw: gateway address (array of 4 integers)  
    # - sn: subnet mask (array of 4 integers)
    
    ip_config = primary_interface.get('ip')
    gw_config = primary_interface.get('gw') 
    sn_config = primary_interface.get('sn')
    
    # Check if IP is configured as a non-zero array
    if not _is_valid_ip_array(ip_config):
        return False
        
    # Check if gateway is configured as a non-zero array
    if not _is_valid_ip_array(gw_config):
        return False
        
    # Check if subnet mask is configured as a non-zero array
    if not _is_valid_ip_array(sn_config):
        return False
    
    # All static IP components are present and valid
    return True

def _is_valid_ip_array(ip_array) -> bool:
    """
    Check if an IP address array is valid and not all zeros.
    
    Args:
        ip_array: Array that should contain 4 integers representing IP octets
        
    Returns:
        bool: True if valid non-zero IP array, False otherwise
    """
    if not isinstance(ip_array, list):
        return False
    
    if len(ip_array) != 4:
        return False
    
    # Check if all elements are integers
    if not all(isinstance(octet, int) for octet in ip_array):
        return False
    
    # Check if all elements are valid IP octets (0-255)
    if not all(0 <= octet <= 255 for octet in ip_array):
        return False
    
    # Check if not all zeros (which would indicate DHCP/no static config)
    if all(octet == 0 for octet in ip_array):
        return False
    
    return True

def get_static_ip_info(config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extract static IP configuration details from WLED config.
    
    Args:
        config: The WLED device configuration dictionary
        
    Returns:
        Dict with static IP info or None if not configured
    """
    if not detect_static_ip_config(config):
        return None
        
    nw_config = config.get('nw', {})
    interfaces = nw_config.get('ins', [])
    
    if not interfaces:
        return None
        
    primary_interface = interfaces[0]
    
    return {
        'ip': primary_interface.get('ip'),
        'gateway': primary_interface.get('gw'),
        'subnet_mask': primary_interface.get('sn'),
        'ip_string': '.'.join(map(str, primary_interface.get('ip', []))),
        'gateway_string': '.'.join(map(str, primary_interface.get('gw', []))),
        'subnet_mask_string': '.'.join(map(str, primary_interface.get('sn', [])))
    }