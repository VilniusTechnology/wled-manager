from typing import Any, Dict, List, Optional
import datetime
from .connection import get_connection
from .models import WLEDDevice

def insert_or_update_wled_device(device: WLEDDevice):
    with get_connection() as conn:
        # Check if device exists
        cur = conn.execute('SELECT id FROM wled_devices WHERE mac = ?', (device.mac,))
        exists = cur.fetchone()

        if exists:
            # Update existing device - only update fields that are provided
            update_fields = []
            values = []

            if device.last_ip is not None:
                update_fields.append('last_ip = ?')
                values.append(device.last_ip)
            if device.hostname is not None:
                update_fields.append('hostname = ?')
                values.append(device.hostname)
            if device.name is not None:
                update_fields.append('name = ?')
                values.append(device.name)
            if device.adopted is not None:
                update_fields.append('adopted = ?')
                values.append(device.adopted)

            # New fields
            if device.software_version is not None:
                update_fields.append('software_version = ?')
                values.append(device.software_version)
            if device.wifi_signal is not None:
                update_fields.append('wifi_signal = ?')
                values.append(device.wifi_signal)
            if device.state_on is not None:
                update_fields.append('state_on = ?')
                values.append(device.state_on)
            if device.architecture is not None:
                update_fields.append('architecture = ?')
                values.append(device.architecture)
            if device.led_count is not None:
                update_fields.append('led_count = ?')
                values.append(device.led_count)
            if device.has_static_ip is not None:
                update_fields.append('has_static_ip = ?')
                values.append(device.has_static_ip)
            if device.wifi_sleep is not None:
                update_fields.append('wifi_sleep = ?')
                values.append(device.wifi_sleep)
            if device.usermod_url is not None:
                update_fields.append('usermod_url = ?')
                values.append(device.usermod_url)

            # Always update last_seen and updated timestamp
            update_fields.append('last_seen = ?')
            values.append(device.last_seen or datetime.datetime.utcnow())
            update_fields.append('updated = CURRENT_TIMESTAMP')

            values.append(device.mac)  # For WHERE clause

            if update_fields:
                query = f'''
                    UPDATE wled_devices SET {', '.join(update_fields)}
                    WHERE mac = ?
                '''
                conn.execute(query, values)
        else:
            # Insert new device
            insert_fields = [
                'id', 'mac', 'last_ip', 
                'name', 
                'hostname', 'name', 'adopted', 'last_seen', 'status', 
                'software_version', 'wifi_signal', 'state_on', 'architecture', 'led_count', 'has_static_ip',
                'wifi_sleep', 'usermod_url',
                'created', 'updated']
            values = [
                device.id, 
                device.mac, 
                device.last_ip, 
                device.name,
                device.hostname, 
                device.name, 
                device.adopted, 
                device.last_seen or datetime.datetime.utcnow(),
                device.status,
                device.software_version,
                device.wifi_signal,
                device.state_on,
                device.architecture,
                device.led_count,
                device.has_static_ip,
                device.wifi_sleep,
                device.usermod_url,
                datetime.datetime.utcnow(),  # created
                datetime.datetime.utcnow()   # updated
            ]
            placeholders = ['?'] * len(insert_fields)

            query = f'''
                INSERT INTO wled_devices ({', '.join(insert_fields)})
                VALUES ({', '.join(placeholders)})
            '''
            conn.execute(query, values)
        conn.commit()

def update_wled_device_partial(updates: Dict[str, Any], mac: str):
    """Update only the changed fields of an existing WLED device."""
    with get_connection() as conn:
        # Build dynamic update query based on provided fields
        update_fields = []
        values = []

        if 'last_ip' in updates:
            update_fields.append('last_ip = ?')
            values.append(updates['last_ip'])
        if 'hostname' in updates:
            update_fields.append('hostname = ?')
            values.append(updates['hostname'])
        if 'name' in updates:
            update_fields.append('name = ?')
            values.append(updates['name'])
        if 'adopted' in updates:
            update_fields.append('adopted = ?')
            values.append(updates['adopted'])
        if 'local_name' in updates:
            update_fields.append('local_name = ?')
            values.append(updates['local_name'])
        if 'status' in updates:
            update_fields.append('status = ?')
            values.append(updates['status'])
        
        # New fields
        if 'software_version' in updates:
            update_fields.append('software_version = ?')
            values.append(updates['software_version'])
        if 'wifi_signal' in updates:
            update_fields.append('wifi_signal = ?')
            values.append(updates['wifi_signal'])
        if 'state_on' in updates:
            update_fields.append('state_on = ?')
            values.append(updates['state_on'])
        if 'architecture' in updates:
            update_fields.append('architecture = ?')
            values.append(updates['architecture'])
        if 'led_count' in updates:
            update_fields.append('led_count = ?')
            values.append(updates['led_count'])
        if 'has_static_ip' in updates:
            update_fields.append('has_static_ip = ?')
            values.append(updates['has_static_ip'])
        if 'wifi_sleep' in updates:
            update_fields.append('wifi_sleep = ?')
            values.append(updates['wifi_sleep'])
        if 'usermod_url' in updates:
            update_fields.append('usermod_url = ?')
            values.append(updates['usermod_url'])

        # Always update last_seen and updated timestamp
        update_fields.append('last_seen = ?')
        values.append(updates.get('last_seen', datetime.datetime.utcnow()))
        update_fields.append('updated = CURRENT_TIMESTAMP')

        values.append(mac)  # For WHERE clause

        if update_fields:
            query = f'''
                UPDATE wled_devices SET {', '.join(update_fields)}
                WHERE mac = ?
            '''
            conn.execute(query, values)
            conn.commit()

def get_wled_device(mac: str) -> Optional[WLEDDevice]:
    """Get a WLED device by MAC address."""
    with get_connection() as conn:
        cur = conn.execute('SELECT * FROM wled_devices WHERE mac = ?', (mac,))
        row = cur.fetchone()
        if row:
            columns = [desc[0] for desc in cur.description]
            data = dict(zip(columns, row))
            
            # Convert boolean fields from SQLite
            if 'adopted' in data:
                if isinstance(data['adopted'], str):
                    data['adopted'] = data['adopted'].lower() in ('1', 'true', 'yes', 'on')
                elif isinstance(data['adopted'], int):
                    data['adopted'] = bool(data['adopted'])
            
            if 'state_on' in data and isinstance(data['state_on'], int):
                data['state_on'] = bool(data['state_on'])
                
            if 'has_static_ip' in data and isinstance(data['has_static_ip'], int):
                data['has_static_ip'] = bool(data['has_static_ip'])

            if 'wifi_sleep' in data and isinstance(data['wifi_sleep'], int):
                data['wifi_sleep'] = bool(data['wifi_sleep'])
            
            return WLEDDevice(**data)
        return None

def get_wled_device_by_ip(ip: str) -> Optional[WLEDDevice]:
    """Get a WLED device by IP address."""
    with get_connection() as conn:
        cur = conn.execute('SELECT * FROM wled_devices WHERE last_ip = ?', (ip,))
        row = cur.fetchone()
        if row:
            columns = [desc[0] for desc in cur.description]
            data = dict(zip(columns, row))
            
            # Convert boolean fields from SQLite
            if 'adopted' in data:
                if isinstance(data['adopted'], str):
                    data['adopted'] = data['adopted'].lower() in ('1', 'true', 'yes', 'on')
                elif isinstance(data['adopted'], int):
                    data['adopted'] = bool(data['adopted'])
            
            if 'state_on' in data and isinstance(data['state_on'], int):
                data['state_on'] = bool(data['state_on'])
                
            if 'has_static_ip' in data and isinstance(data['has_static_ip'], int):
                data['has_static_ip'] = bool(data['has_static_ip'])

            if 'wifi_sleep' in data and isinstance(data['wifi_sleep'], int):
                data['wifi_sleep'] = bool(data['wifi_sleep'])
            
            return WLEDDevice(**data)
        return None

def get_wled_device_by_id(device_id: str) -> Optional[WLEDDevice]:
    """Get a WLED device by device_id."""
    with get_connection() as conn:
        cur = conn.execute('SELECT * FROM wled_devices WHERE id = ?', (device_id,))
        row = cur.fetchone()
        if row:
            columns = [desc[0] for desc in cur.description]
            data = dict(zip(columns, row))
            
            # Convert boolean fields from SQLite
            if 'adopted' in data:
                if isinstance(data['adopted'], str):
                    data['adopted'] = data['adopted'].lower() in ('1', 'true', 'yes', 'on')
                elif isinstance(data['adopted'], int):
                    data['adopted'] = bool(data['adopted'])
                    
            if 'state_on' in data and isinstance(data['state_on'], int):
                data['state_on'] = bool(data['state_on'])
                
            if 'has_static_ip' in data and isinstance(data['has_static_ip'], int):
                data['has_static_ip'] = bool(data['has_static_ip'])

            if 'wifi_sleep' in data and isinstance(data['wifi_sleep'], int):
                data['wifi_sleep'] = bool(data['wifi_sleep'])
            
            return WLEDDevice(**data)
        return None

def get_all_wled_devices() -> List[WLEDDevice]:
    """Get all WLED devices."""
    with get_connection() as conn:
        cur = conn.execute('SELECT * FROM wled_devices')
        rows = cur.fetchall()
        if rows:
            columns = [desc[0] for desc in cur.description]
            devices = []
            for row in rows:
                data = dict(zip(columns, row))
                
                # Convert boolean fields from SQLite
                if 'adopted' in data:
                    if isinstance(data['adopted'], str):
                        data['adopted'] = data['adopted'].lower() in ('1', 'true', 'yes', 'on')
                    elif isinstance(data['adopted'], int):
                        data['adopted'] = bool(data['adopted'])
                
                if 'state_on' in data and isinstance(data['state_on'], int):
                    data['state_on'] = bool(data['state_on'])
                    
                if 'has_static_ip' in data and isinstance(data['has_static_ip'], int):
                    data['has_static_ip'] = bool(data['has_static_ip'])

                if 'wifi_sleep' in data and isinstance(data['wifi_sleep'], int):
                    data['wifi_sleep'] = bool(data['wifi_sleep'])
                
                devices.append(WLEDDevice(**data))
            return devices
        return []

def delete_wled_device(device_id: str) -> bool:
    """Delete a WLED device and all its associated data."""
    with get_connection() as conn:
        try:
            # Delete associated data first (if no CASCADE set up)
            conn.execute('DELETE FROM wled_configs WHERE device_id = ?', (device_id,))
            conn.execute('DELETE FROM wled_configs_versions WHERE device_id = ?', (device_id,))
            conn.execute('DELETE FROM wled_backups WHERE device_id = ?', (device_id,))
            
            # Delete the device itself
            cursor = conn.execute('DELETE FROM wled_devices WHERE id = ?', (device_id,))
            conn.commit()
            
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting device {device_id}: {e}")
            return False
