import os
import sqlite3
import json
import uuid
from typing import Dict, Any

def get_app_config():
    """Get the app config settings."""
    # Ensure database directory exists
    os.makedirs("database", exist_ok=True)
    db_path = "database/wled_devices.db"  # Use default to avoid recursion
    if not os.path.exists(db_path):
        return {}
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.execute('SELECT settings FROM app_config LIMIT 1')
        row = cur.fetchone()
        if row:
            return json.loads(row[0])
    except sqlite3.OperationalError:
        # Table doesn't exist yet
        pass
    finally:
        conn.close()
    return {}

def set_app_config(settings: Dict[str, Any]):
    """Set the app config settings."""
    settings_json = json.dumps(settings)
    # Ensure database directory exists
    os.makedirs("database", exist_ok=True)
    db_path = "database/wled_devices.db"  # Use default to avoid recursion
    conn = sqlite3.connect(db_path)
    try:
        # Delete existing
        conn.execute('DELETE FROM app_config')
        # Insert new
        config_id = str(uuid.uuid4())
        conn.execute('INSERT INTO app_config (id, settings) VALUES (?, ?)', (config_id, settings_json))
        conn.commit()
    except sqlite3.OperationalError:
        # Table doesn't exist yet, this shouldn't happen if init_db is called properly
        pass
    finally:
        conn.close()
