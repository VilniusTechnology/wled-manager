import json
import os
from db.sqlite import get_app_config, set_app_config

def _get_default_settings():
    """Get default settings with environment variable overrides."""
    return {
        "scan_timeout": 0.5,
        "info_timeout": 1,
        "backup_info_timeout": 5,
        "backup_download_timeout": 10,
        "db_path": os.getenv("DATABASE_PATH", "database/wled_devices.db"),
        "backup_dir": os.getenv("BACKUP_DIR", "backups"),
        "health_check_interval_seconds": 60,
        "network_scan_interval_hours": 168, # 7 days
        "device_refresh_interval_hours": 1,
        "backup_interval_hours": 24,
        "backup_retention_days": 30,
        "backup_retention_count": 10,
        "max_workers": 32,
        "connection_pool_size": 20,
        "max_retries": 1,
        "scheduler_initial_delay": 120,
        "network_range": os.getenv("NETWORK_RANGE", "192.168.1.0/24"),
        "disable_network_scan": os.getenv("DISABLE_NETWORK_SCAN", "false").lower() == "true",
        "disable_device_refresh": os.getenv("DISABLE_DEVICE_REFRESH", "false").lower() == "true",
        "disable_backup": os.getenv("DISABLE_BACKUP", "false").lower() == "true",
        "disable_health_check": os.getenv("DISABLE_HEALTH_CHECK", "false").lower() == "true",
        "backup_email_enabled": os.getenv("BACKUP_EMAIL_ENABLED", "true").lower() == "true"
    }

# For backwards compatibility
DEFAULT_SETTINGS = _get_default_settings()

def get_setting(key: str):
    """Get a single setting value."""
    # Always get fresh defaults to pick up environment variable changes
    defaults = _get_default_settings()
    
    settings = get_app_config()
    if not settings:
        # Initialize with defaults
        set_app_config(defaults)
        settings = defaults
    return settings.get(key, defaults.get(key))

def set_setting(key: str, value):
    """Set a single setting value."""
    settings = get_app_config()
    if not settings:
        settings = _get_default_settings().copy()
    settings[key] = value
    set_app_config(settings)

    return settings

def get_all_settings():
    """Get all settings, merging stored values with defaults."""
    defaults = _get_default_settings()
    settings = get_app_config()
    
    if not settings:
        set_app_config(defaults)
        return defaults
        
    # Merge stored settings into defaults to ensure all keys exist
    # (Stored values override defaults)
    merged_settings = defaults.copy()
    merged_settings.update(settings)
    
    return merged_settings

def set_all_settings(settings: dict):
    """Set all settings, merging with existing ones."""
    current_settings = get_all_settings()
    current_settings.update(settings)
    set_app_config(current_settings)
