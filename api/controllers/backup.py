from fastapi import APIRouter
from typing import Dict, List
from collections import defaultdict
import logging
from db.sqlite import get_connection
from db.backup_models import WLEDBackupDBModel
from models.dto import WLEDBackupDTO
import os
from fastapi.responses import FileResponse
from api.services.backup_service import get_backup_file_path

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/backups", response_model=Dict[str, List[WLEDBackupDTO]], summary="List all backups grouped by MAC address")
def list_backups():
    """
    List all backups, grouped by MAC address.
    """
    logger.info("Retrieving all backups from database")
    
    with get_connection() as conn:
        cursor = conn.execute("SELECT id, mac, timestamp, presets_path, cfg_path FROM wled_backups")
        rows = cursor.fetchall()
    
    logger.debug(f"Found {len(rows)} backup records in database")
    
    grouped = defaultdict(list)
    for row in rows:
        backup = WLEDBackupDBModel(
            id=row[0],
            mac=row[1],
            timestamp=row[2],
            presets_path=row[3],
            cfg_path=row[4]
        )
        grouped[backup.mac].append(WLEDBackupDTO(**backup.dict()))
    
    logger.info(f"Grouped backups into {len(grouped)} MAC addresses")
    for mac, backups in grouped.items():
        logger.debug(f"MAC {mac}: {len(backups)} backups")
    
    return grouped

@router.get("/backups/download/{backup_id}/config", summary="Download config file for a backup")
def download_config(backup_id: str):
    """
    Download the config file for a specific backup.
    """
    logger.info(f"Downloading config for backup {backup_id}")
    
    try:
        file_path = get_backup_file_path(backup_id, "config")
        return FileResponse(
            path=file_path,
            filename=f"config_{backup_id}.json",
            media_type="application/json"
        )
    except ValueError as e:
        return {"error": str(e)}

@router.get("/backups/{backup_id}/config-content", summary="Get config content as JSON for comparison")
def get_config_content(backup_id: str):
    """
    Get the config file content as JSON for comparison purposes.
    """
    logger.info(f"Getting config content for backup {backup_id}")
    
    try:
        file_path = get_backup_file_path(backup_id, "config")
        
        # Read and parse JSON content
        import json
        with open(file_path, 'r') as f:
            config_content = json.load(f)
        
        return config_content
    except ValueError as e:
        return {"error": str(e)}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file {file_path}: {e}")
        return {"error": "Invalid JSON in config file"}
    except Exception as e:
        logger.error(f"Error reading config file: {e}")
        return {"error": "Failed to read config file"}

@router.get("/backups/download/{backup_id}/presets", summary="Download presets file for a backup")
def download_presets(backup_id: str):
    """
    Download the presets file for a specific backup.
    """
    logger.info(f"Downloading presets for backup {backup_id}")
    
    try:
        file_path = get_backup_file_path(backup_id, "presets")
        return FileResponse(
            path=file_path,
            filename=f"presets_{backup_id}.json",
            media_type="application/json"
        )
    except ValueError as e:
        return {"error": str(e)}
