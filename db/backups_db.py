from typing import List, Optional
from .connection import get_connection
from .backup_models import WLEDBackupDBModel

def insert_backup(backup: WLEDBackupDBModel):
    with get_connection() as conn:
        conn.execute('''
            INSERT INTO wled_backups (id, mac, timestamp, presets_path, cfg_path, device_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            backup.id,
            backup.mac,
            backup.timestamp,
            backup.presets_path,
            backup.cfg_path,
            backup.device_id
        ))
        conn.commit()

def get_backups_for_device(mac: str) -> List[WLEDBackupDBModel]:
    """Get all backups for a specific device."""
    with get_connection() as conn:
        cur = conn.execute(
            'SELECT id, mac, timestamp, presets_path, cfg_path, device_id FROM wled_backups WHERE mac = ? ORDER BY timestamp DESC', 
            (mac,)
        )
        rows = cur.fetchall()
        backups = []
        for row in rows:
            backup = WLEDBackupDBModel(
                id=row[0],
                mac=row[1],
                timestamp=row[2],
                presets_path=row[3],
                cfg_path=row[4],
                device_id=row[5]
            )
            backups.append(backup)
        return backups

def delete_backup(backup_id: str) -> bool:
    """Delete a backup record from the database."""
    with get_connection() as conn:
        try:
            conn.execute('DELETE FROM wled_backups WHERE id = ?', (backup_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting backup {backup_id}: {e}")
            return False

def device_has_backups(mac: str) -> bool:
    """Check if a device has any backups."""
    with get_connection() as conn:
        cur = conn.execute('SELECT COUNT(*) FROM wled_backups WHERE mac = ?', (mac,))
        row = cur.fetchone()
        return row[0] > 0 if row else False

def get_backup_by_id(backup_id: str) -> Optional[WLEDBackupDBModel]:
    """Get a backup by its ID."""
    with get_connection() as conn:
        cursor = conn.execute('''
            SELECT id, mac, timestamp, presets_path, cfg_path, device_id
            FROM wled_backups
            WHERE id = ?
        ''', (backup_id,))
        
        row = cursor.fetchone()
        if row:
            return WLEDBackupDBModel(
                id=row[0],
                mac=row[1],
                timestamp=row[2],
                presets_path=row[3],
                cfg_path=row[4],
                device_id=row[5]
            )
        return None
