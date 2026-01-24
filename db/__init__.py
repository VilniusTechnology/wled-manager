import os
from .connection import get_db_path, create_table, get_connection
from .devices_db import (
    insert_or_update_wled_device, 
    update_wled_device_partial, 
    get_wled_device, 
    get_wled_device_by_ip, 
    get_wled_device_by_id, 
    get_all_wled_devices, 
    delete_wled_device
)
from .backups_db import (
    insert_backup, 
    get_backups_for_device, 
    delete_backup, 
    device_has_backups, 
    get_backup_by_id
)
from .versions_db import (
    insert_device_version, 
    upsert_device_config, 
    create_device_version, 
    get_latest_device_info, 
    get_latest_device_info_map
)
from .settings_db import get_app_config, set_app_config
from .passwords_db import store_password, get_password_by_key, get_decrypted_password

# Re-export models for convenience
from .models import WLEDDevice, WLEDDeviceVersion, WLEDDeviceDBModel
from .backup_models import WLEDBackupDBModel

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Call this function at app startup to ensure the database and tables exist
def init_db():
    from services.settings_service import get_all_settings
    db_path = get_db_path()
    if not os.path.exists(db_path):
        print(f"Database file '{db_path}' not found. Creating it...")
    create_table()
    # Initialize settings
    get_all_settings()
    # Mark database as initialized
    import db.connection
    db.connection.DB_INITIALIZED = True
    print("Database initialized successfully.")
