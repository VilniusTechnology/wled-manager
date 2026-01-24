"""
This module provides a validator to ensure sync settings are stored as proper boolean values.
"""

def validate_sync_config(cfg_full):
    """
    Validates and converts sync configuration values to proper booleans.
    Args:
        cfg_full (dict): The full configuration dictionary
    Returns:
        dict: The validated configuration dictionary
    """
    if not isinstance(cfg_full, dict):
        return cfg_full
        
    if_config = cfg_full.get('if', {})
    sync_config = if_config.get('sync', {})
    recv_config = sync_config.get('recv', {})
    
    if recv_config and isinstance(recv_config, dict):
        # Convert any integer values to boolean
        for key, value in recv_config.items():
            # Skip 'grp' as it is a bitmask (integer), not a boolean
            if key == 'grp':
                # Preserve the original value
                recv_config[key] = value
                continue
                
            if isinstance(value, (int, str)):
                if isinstance(value, int):
                    recv_config[key] = bool(value)
                elif isinstance(value, str):
                    value = value.lower().strip()
                    if value in ('true', '1', 'yes', 'on'):
                        recv_config[key] = True
                    elif value in ('false', '0', 'no', 'off'):
                        recv_config[key] = False
        
        sync_config['recv'] = recv_config
        if_config['sync'] = sync_config
        cfg_full['if'] = if_config
    
    return cfg_full