from fastapi import APIRouter, HTTPException
from typing import Dict, List
from collections import defaultdict
import logging
import json
from db.sqlite import get_connection
from db.models import WLEDDeviceVersion
from models.dto import WLEDDeviceVersionDTO

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/config-versions", response_model=Dict[str, List[Dict]], summary="List all config versions grouped by MAC address")
def list_config_versions():
    """
    List all config versions from wled_configs_versions table, grouped by MAC address.
    """
    logger.info("Retrieving all config versions from database")
    
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT cv.version_id, cv.mac, cv.timestamp, cv.ip, cv.device_id, cv.cfg_full, wd.name
            FROM wled_configs_versions cv
            LEFT JOIN wled_devices wd ON cv.device_id = wd.id
            ORDER BY cv.mac, cv.timestamp DESC
        """)
        rows = cursor.fetchall()
    
    logger.debug(f"Found {len(rows)} config version records in database")
    
    grouped = defaultdict(list)
    for row in rows:
        version_info = {
            "version_id": row[0],
            "mac": row[1], 
            "timestamp": row[2],
            "ip": row[3],
            "device_id": row[4],
            "has_config": bool(row[5]),  # Check if cfg_full is not null/empty
            "device_name": row[6] or f"Device {row[1]}"  # Use device name or fallback
        }
        grouped[row[1]].append(version_info)
    
    logger.info(f"Grouped config versions into {len(grouped)} MAC addresses")
    for mac, versions in grouped.items():
        logger.debug(f"MAC {mac}: {len(versions)} versions")
    
    return grouped

@router.get("/config-versions/{version_id}/config", summary="Get config content for a specific version")
def get_config_version_content(version_id: str):
    """
    Get the config content from a specific config version for comparison purposes.
    """
    logger.info(f"Getting config content for version {version_id}")
    
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT cfg_full, mac, timestamp, ip 
            FROM wled_configs_versions 
            WHERE version_id = ?
        """, (version_id,))
        row = cursor.fetchone()
    
    if not row:
        logger.error(f"Config version {version_id} not found")
        raise HTTPException(status_code=404, detail="Config version not found")
    
    cfg_full, mac, timestamp, ip = row
    
    if not cfg_full:
        logger.error(f"No config data found for version {version_id}")
        raise HTTPException(status_code=404, detail="No config data available for this version")
    
    try:
        # Parse the JSON config
        config_content = json.loads(cfg_full)
        
        # Return config with metadata
        return {
            "version_id": version_id,
            "mac": mac,
            "timestamp": timestamp,
            "ip": ip,
            "config": config_content
        }
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config for version {version_id}: {e}")
        raise HTTPException(status_code=500, detail="Invalid JSON in config data")
    except Exception as e:
        logger.error(f"Error reading config for version {version_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to read config data")

@router.get("/devices/{device_id}/config-versions", summary="Get all config versions for a specific device")
def get_device_config_versions(device_id: str):
    """
    Get all config versions for a specific device.
    """
    logger.info(f"Getting config versions for device {device_id}")
    
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT cv.version_id, cv.mac, cv.timestamp, cv.ip, cv.cfg_full, wd.name
            FROM wled_configs_versions cv
            LEFT JOIN wled_devices wd ON cv.device_id = wd.id
            WHERE cv.device_id = ?
            ORDER BY cv.timestamp DESC
        """, (device_id,))
        rows = cursor.fetchall()
    
    if not rows:
        logger.info(f"No config versions found for device {device_id}")
        return []
    
    versions = []
    for row in rows:
        version_info = {
            "version_id": row[0],
            "mac": row[1],
            "timestamp": row[2], 
            "ip": row[3],
            "has_config": bool(row[4]),
            "device_name": row[5] or f"Device {row[1]}"
        }
        versions.append(version_info)
    
    logger.info(f"Found {len(versions)} config versions for device {device_id}")
    return versions