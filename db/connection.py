import sqlite3
import os
import sys

DB_PATH = None
DB_INITIALIZED = False

def get_db_path():
    global DB_PATH, DB_INITIALIZED
    if DB_PATH is None or not DB_INITIALIZED:
        try:
            from services.settings_service import get_setting
            DB_PATH = get_setting("db_path")
            # Robustness: If the user provided a directory path, append a default filename
            # This handles the case where DATABASE_PATH=/app/database (directory) instead of a file
            if os.path.isdir(DB_PATH) or (not os.path.splitext(DB_PATH)[1]):
                # It's a directory or has no extension (likely a directory path)
                # But we should be careful not to treat a file without extension as a dir if it doesn't already exist as a dir
                # Safer check: if it ends in slash or is an existing directory
                if DB_PATH.endswith(os.path.sep) or os.path.isdir(DB_PATH):
                     DB_PATH = os.path.join(DB_PATH, "wled_devices.db")
            
            DB_INITIALIZED = True
        except (RecursionError, ImportError):
            # Use default if there's a circular import or recursion
            DB_PATH = "database/wled_devices.db"
    
    # Ensure the database directory exists
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    
    return DB_PATH

def get_connection():
    conn = sqlite3.connect(get_db_path(), timeout=30.0)
    # Enable Write-Ahead Logging for better concurrency
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn

def create_table():
    with get_connection() as conn:
        # Rename old table if exists and new table doesn't
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='wled_devices'")
        if cursor.fetchone():
            cursor2 = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='wled_configs'")
            if not cursor2.fetchone():
                conn.execute("ALTER TABLE wled_devices RENAME TO wled_configs")
        
        # Rename old versions table if exists and new table doesn't
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='wled_device_versions'")
        if cursor.fetchone():
            cursor2 = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='wled_configs_versions'")
            if not cursor2.fetchone():
                conn.execute("ALTER TABLE wled_device_versions RENAME TO wled_configs_versions")
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS wled_configs (
                id TEXT PRIMARY KEY,
                mac TEXT NOT NULL,
                mac_original TEXT NOT NULL,
                ip TEXT NOT NULL,
                mqtt TEXT,
                network TEXT,
                cfg_full TEXT,
                info_full TEXT,
                state_full TEXT,
                device_id TEXT NOT NULL,
                FOREIGN KEY (device_id) REFERENCES wled_devices(id)
            )
        ''')
        # Versioned table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS wled_configs_versions (
                version_id TEXT PRIMARY KEY,
                mac TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                ip TEXT NOT NULL,
                mqtt TEXT,
                network TEXT,
                cfg_full TEXT,
                info_full TEXT,
                state_full TEXT,
                device_id TEXT NOT NULL,
                FOREIGN KEY (device_id) REFERENCES wled_devices(id)
            )
        ''')
        # Backup reference table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS wled_backups (
                id TEXT PRIMARY KEY,
                mac TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                presets_path TEXT NOT NULL,
                cfg_path TEXT NOT NULL,
                device_id TEXT NOT NULL,
                FOREIGN KEY (device_id) REFERENCES wled_devices(id)
            )
        ''')
        # New wled_devices table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS wled_devices (
                id TEXT PRIMARY KEY,
                mac TEXT NOT NULL UNIQUE,
                last_ip TEXT,
                local_name TEXT,
                hostname TEXT,
                name TEXT,
                adopted BOOLEAN DEFAULT FALSE,
                last_seen DATETIME,
                status TEXT,
                created DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # App config table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS app_config (
                id TEXT PRIMARY KEY,
                settings TEXT NOT NULL
            )
        ''')

        # Passwords table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        
        # Add device_id column to existing tables if not exists
        tables_to_alter = ['wled_configs', 'wled_configs_versions', 'wled_backups']
        for table in tables_to_alter:
            try:
                conn.execute(f'ALTER TABLE {table} ADD COLUMN device_id TEXT NOT NULL')
            except sqlite3.OperationalError:
                pass  # Column already exists
            try:
                conn.execute(f'ALTER TABLE {table} ADD CONSTRAINT fk_{table}_device_id FOREIGN KEY (device_id) REFERENCES wled_devices(id)')
            except sqlite3.OperationalError:
                pass  # Constraint already exists
        
        # Add hostname and name columns to wled_devices if not exists
        try:
            conn.execute('ALTER TABLE wled_devices ADD COLUMN hostname TEXT')
        except sqlite3.OperationalError:
            pass
        try:
            conn.execute('ALTER TABLE wled_devices ADD COLUMN name TEXT')
        except sqlite3.OperationalError:
            pass
        # Add status column to wled_devices if not exists
        try:
            conn.execute('ALTER TABLE wled_devices ADD COLUMN status TEXT')
        except sqlite3.OperationalError:
            pass

        # Add performance optimization columns
        new_columns = {
            'software_version': 'TEXT',
            'wifi_signal': 'INTEGER',
            'state_on': 'BOOLEAN',
            'architecture': 'TEXT',
            'led_count': 'INTEGER',
            'has_static_ip': 'BOOLEAN',
            'wifi_sleep': 'BOOLEAN',
            'turn_on_after_power_up': 'BOOLEAN',
            'mqtt_enabled': 'BOOLEAN'
        }
        
        for col, type_ in new_columns.items():
            try:
                conn.execute(f'ALTER TABLE wled_devices ADD COLUMN {col} {type_}')
            except sqlite3.OperationalError:
                pass
        
        # Add usermod_url column
        try:
            conn.execute('ALTER TABLE wled_devices ADD COLUMN usermod_url TEXT')
        except sqlite3.OperationalError:
            pass
        
        conn.commit()
