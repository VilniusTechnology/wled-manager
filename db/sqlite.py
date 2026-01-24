from .models import WLEDDeviceDBModel, WLEDDevice, WLEDDeviceVersion
from .backup_models import WLEDBackupDBModel

# Connection & Setup
from .connection import (
    get_db_path, 
    get_connection, 
    create_table, 
    DB_PATH, 
    DB_INITIALIZED
)

# Device operations
from .devices_db import (
    insert_or_update_wled_device,
    update_wled_device_partial,
    get_wled_device,
    get_wled_device_by_ip,
    get_wled_device_by_id,
    delete_wled_device,
    get_all_wled_devices
)

# Backup operations
from .backups_db import (
    insert_backup,
    delete_backup,
    get_backups_for_device,
    get_backup_by_id,
    device_has_backups
)

# Version/Config operations
from .versions_db import (
    insert_device_version,
    upsert_device_config,
    create_device_version,
    get_latest_device_info,
    get_latest_device_info_map
)

# Settings operations
from .settings_db import (
    get_app_config,
    set_app_config
)

# Password operations
from .passwords_db import (
    store_password,
    get_password_by_key,
    get_decrypted_password
)
