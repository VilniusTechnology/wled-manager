from .models import WLEDDeviceDBModel, WLEDDeviceVersion
import json
import uuid
from datetime import datetime
import hashlib

def dto_to_db_model(mac: str, mac_original: str, ip: str, cfg_full, info_full, state_full):
    # Handle both dict and DTO object for cfg_full
    mqtt = None
    network = None
    iface = None
    if hasattr(cfg_full, 'iface'):
        iface = cfg_full.iface
    elif isinstance(cfg_full, dict):
        iface = cfg_full.get('if', None)
    if iface and isinstance(iface, dict):
        mqtt = iface.get('mqtt', None)
    network = cfg_full.get('nw', None) if isinstance(cfg_full, dict) else getattr(cfg_full, 'nw', None)

    return WLEDDeviceDBModel(
        id=str(uuid.uuid4()),
        mac=mac,
        mac_original=mac_original,
        ip=ip,
        mqtt=json.dumps(mqtt) if mqtt else None,
        network=json.dumps(network) if network else None,
        cfg_full=json.dumps(cfg_full.to_dict() if hasattr(cfg_full, 'to_dict') else cfg_full),
        info_full=json.dumps(info_full.to_dict() if hasattr(info_full, 'to_dict') else info_full),
        state_full=json.dumps(state_full.to_dict() if hasattr(state_full, 'to_dict') else state_full),
        device_id=hashlib.md5(mac.encode()).hexdigest()
    )

def dto_to_device_version_model(mac: str, mac_original: str, ip: str, cfg_full, info_full, state_full, version_id: str = None):
    # Handle both dict and DTO object for cfg_full
    mqtt = None
    network = None
    iface = None
    if hasattr(cfg_full, 'iface'):
        iface = cfg_full.iface
    elif isinstance(cfg_full, dict):
        iface = cfg_full.get('if', None)
    if iface and isinstance(iface, dict):
        mqtt = iface.get('mqtt', None)
    network = cfg_full.get('nw', None) if isinstance(cfg_full, dict) else getattr(cfg_full, 'nw', None)

    return WLEDDeviceVersion(
        version_id=version_id or str(uuid.uuid4()),
        mac=mac,
        timestamp=datetime.utcnow(),
        ip=ip,
        mqtt=json.dumps(mqtt) if mqtt else None,
        network=json.dumps(network) if network else None,
        cfg_full=json.dumps(cfg_full.to_dict() if hasattr(cfg_full, 'to_dict') else cfg_full),
        info_full=json.dumps(info_full.to_dict() if hasattr(info_full, 'to_dict') else info_full),
        state_full=json.dumps(state_full.to_dict() if hasattr(state_full, 'to_dict') else state_full),
    )
