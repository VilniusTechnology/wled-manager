"""
Utility functions for normalizing WLED config values.
"""
from typing import Any, Dict, Union

def normalize_bool_value(value: Any) -> bool:
    """
    Normalize various input types to a boolean value.
    
    Args:
        value: The value to normalize (bool, int, str)
        
    Returns:
        bool: The normalized boolean value
        
    Raises:
        ValueError: If the value cannot be converted to a boolean
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return bool(value)
    if isinstance(value, str):
        value = value.lower().strip()
        if value in ('true', '1', 'yes', 'on'):
            return True
        if value in ('false', '0', 'no', 'off'):
            return False
    raise ValueError(f'Invalid boolean value: {value}')

def normalize_sync_recv_values(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize sync.recv values in WLED config to proper booleans.
    
    Args:
        config: The WLED configuration dictionary
        
    Returns:
        Dict[str, Any]: The configuration with normalized sync.recv values
    """
    if not isinstance(config, dict):
        return config
        
    if_config = config.get('if', {})
    if not isinstance(if_config, dict):
        return config
        
    sync_config = if_config.get('sync', {})
    if not isinstance(sync_config, dict):
        return config
        
    recv_config = sync_config.get('recv', {})
    if not isinstance(recv_config, dict):
        return config
        
    try:
        normalized_recv = {}
        for key, value in recv_config.items():
            # Skip 'grp' as it is a bitmask (integer), not a boolean
            if key == 'grp':
                normalized_recv[key] = value
                continue
                
            try:
                normalized_recv[key] = normalize_bool_value(value)
            except ValueError:
                # Keep the original value if normalization fails
                normalized_recv[key] = value
                
        sync_config['recv'] = normalized_recv
        if_config['sync'] = sync_config
        config['if'] = if_config
        
    except Exception:
        # If anything goes wrong, return the original config
        pass
        
    return config