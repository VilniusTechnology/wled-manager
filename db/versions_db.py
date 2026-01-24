from typing import Dict, Any, Optional
import datetime
import uuid
import json
from .connection import get_connection
from .models import WLEDDeviceDBModel, WLEDDeviceVersion

def insert_device_version(device_version: WLEDDeviceVersion):
    with get_connection() as conn:
        conn.execute('''
            INSERT INTO wled_configs_versions (version_id, mac, timestamp, ip, mqtt, network, cfg_full, info_full, state_full, device_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            device_version.version_id,
            device_version.mac,
            device_version.timestamp.isoformat(),
            device_version.ip,
            device_version.mqtt,
            device_version.network,
            device_version.cfg_full,
            device_version.info_full,
            device_version.state_full,
            device_version.device_id
        ))
        conn.commit()

def upsert_device_config(device: WLEDDeviceDBModel):
    """
    Upsert (update or insert) a WLED device configuration in the wled_configs table.
    If the device exists (based on MAC), updates its configuration; otherwise inserts a new configuration record.
    This function specifically handles the device's configuration data, not the device record itself.
    """
    with get_connection() as conn:
        # Try update first, if no row updated, insert
        cur = conn.execute('''
            UPDATE wled_configs SET
                mac_original = ?,
                ip = ?,
                mqtt = ?,
                network = ?,
                cfg_full = ?,
                info_full = ?,
                state_full = ?,
                device_id = ?
            WHERE mac = ?
        ''', (
            device.mac_original,
            device.ip,
            device.mqtt,
            device.network,
            device.cfg_full,
            device.info_full,
            device.state_full,
            device.device_id,
            device.mac
        ))
        if cur.rowcount == 0:
            conn.execute('''
                INSERT INTO wled_configs (id, mac, mac_original, ip, mqtt, network, cfg_full, info_full, state_full, device_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                device.id,
                device.mac,
                device.mac_original,
                device.ip,
                device.mqtt,
                device.network,
                device.cfg_full,
                device.info_full,
                device.state_full,
                device.device_id
            ))
        conn.commit()

def create_device_version(mac: str, ip: str, cfg_full: str = None, info_full: str = None, state_full: str = None, device_id: str = None) -> str:
    """Create a new version entry for a device."""
    version_id = str(uuid.uuid4())

    device_version = WLEDDeviceVersion(
        version_id=version_id,
        mac=mac,
        timestamp=datetime.datetime.utcnow(),
        ip=ip,
        cfg_full=cfg_full,
        info_full=info_full,
        state_full=state_full,
        device_id=device_id
    )

    insert_device_version(device_version)
    return version_id

def get_latest_device_info(mac: str) -> Optional[Dict[str, Any]]:
    """Get the latest device info from the versions table."""
    with get_connection() as conn:
        cur = conn.execute('''
            SELECT cfg_full, info_full, state_full, ip, timestamp
            FROM wled_configs_versions 
            WHERE mac = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''', (mac,))
        row = cur.fetchone()
        if row:
            try:
                cfg = json.loads(row[0]) if row[0] else {}
                info = json.loads(row[1]) if row[1] else {}
                state = json.loads(row[2]) if row[2] else {}
                return {
                    'cfg': cfg,
                    'info': info,
                    'state': state,
                    'ip': row[3],
                    'timestamp': row[4],
                    'mac': mac
                }
            except json.JSONDecodeError:
                return None
        return None

def get_latest_device_info_map() -> Dict[str, Dict[str, Any]]:
    """Get the latest device info for all devices efficiently."""
    with get_connection() as conn:
        # This query groups by mac and picks the latest timestamp
        cur = conn.execute('''
            SELECT mac, cfg_full, info_full, state_full, ip, timestamp
            FROM wled_configs_versions
            WHERE (mac, timestamp) IN (
                SELECT mac, MAX(timestamp)
                FROM wled_configs_versions
                GROUP BY mac
            )
        ''')
        
        result = {}
        for row in cur.fetchall():
            mac = row[0]
            try:
                cfg = json.loads(row[1]) if row[1] else {}
                info = json.loads(row[2]) if row[2] else {}
                state = json.loads(row[3]) if row[3] else {}
                result[mac] = {
                    'cfg': cfg,
                    'info': info,
                    'state': state,
                    'ip': row[4],
                    'timestamp': row[5],
                    'mac': mac
                }
            except json.JSONDecodeError:
                continue
        return result
