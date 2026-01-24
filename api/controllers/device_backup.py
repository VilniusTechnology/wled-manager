"""
Device backup and restore API endpoints.
Extracted from devices.py for better maintainability.
"""
from fastapi import APIRouter, HTTPException
from typing import List
import os
import logging
import requests

from pydantic import BaseModel
from db.sqlite import get_all_wled_devices, get_backup_by_id
from models.dto import SuccessResponse, MassBackupResponse
from api.services.device_service import get_device_and_validate_ip, upload_file_to_device
from scanner.wled_backup_retriever import WLEDBackupRetriever

router = APIRouter()
logger = logging.getLogger(__name__)


class RestoreRequest(BaseModel):
    backup_id: str
    restore_config: bool = True
    restore_presets: bool = True


class MassBackupRequest(BaseModel):
    backup_config: bool = True
    backup_presets: bool = True


@router.post("/devices/{device_id}/backup", response_model=SuccessResponse, summary="Backup a WLED device")
def backup_device(device_id: str):
    """Backup a WLED device by downloading its config and presets files."""
    logger.info(f"Starting backup for device: {device_id}")
    
    device = get_device_and_validate_ip(device_id)
    
    try:
        backup_retriever = WLEDBackupRetriever()
        backup_dir = backup_retriever.backup_device(device.last_ip)
        
        if backup_dir:
            logger.info(f"Successfully backed up device {device_id} to {backup_dir}")
            return SuccessResponse(success=True, message=f"Device backed up successfully to {backup_dir}")
        else:
            logger.error(f"Failed to backup device {device_id}")
            raise HTTPException(status_code=500, detail="Failed to backup device")
            
    except requests.exceptions.ConnectTimeout:
        logger.error(f"Timeout connecting to device {device_id}")
        raise HTTPException(status_code=408, detail="Connection timed out")
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error backing up device {device_id}")
        raise HTTPException(status_code=503, detail="Device unreachable")
    except OSError as e:
        logger.error(f"File system error backing up device {device_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Backup storage failed: {str(e)}")
    except Exception as e:
        logger.error(f"Error backing up device {device_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Backup failed: {str(e)}")


@router.post("/devices/{device_id}/restore", response_model=SuccessResponse, summary="Restore a WLED device from backup")
async def restore_device(device_id: str, request: RestoreRequest):
    """Restore a WLED device from a backup."""
    logger.info(f"Starting restore for device: {device_id}, backup: {request.backup_id}")
    
    device = get_device_and_validate_ip(device_id)
    
    # Get backup information
    backup = get_backup_by_id(request.backup_id)
    if not backup:
        logger.warning(f"Backup with ID {request.backup_id} not found")
        raise HTTPException(status_code=404, detail=f"Backup with ID {request.backup_id} not found")
    
    # Verify backup belongs to device
    if backup.mac != device.mac:
        logger.warning(f"Backup {request.backup_id} does not belong to device {device_id}")
        raise HTTPException(status_code=400, detail="Backup does not belong to this device")
    
    try:
        files_restored = []
        
        if request.restore_config and backup.cfg_path and os.path.exists(backup.cfg_path):
            logger.info(f"Uploading cfg.json to {device.last_ip}")
            await upload_file_to_device(device.last_ip, backup.cfg_path, "cfg.json")
            files_restored.append("cfg.json")
        
        if request.restore_presets and backup.presets_path and os.path.exists(backup.presets_path):
            logger.info(f"Uploading presets.json to {device.last_ip}")
            await upload_file_to_device(device.last_ip, backup.presets_path, "presets.json")
            files_restored.append("presets.json")
        
        if not files_restored:
            raise HTTPException(status_code=400, detail="No valid files to restore")
        
        logger.info(f"Successfully restored device {device_id}: {', '.join(files_restored)}")
        return SuccessResponse(success=True, message=f"Successfully restored: {', '.join(files_restored)}")
        
    except HTTPException:
        raise
    except HTTPException:
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error restoring device {device_id}: {e}")
        raise HTTPException(status_code=503, detail=f"Network error during restore: {str(e)}")
    except OSError as e:
        logger.error(f"File error restoring device {device_id}: {e}")
        raise HTTPException(status_code=500, detail=f"File error: {str(e)}")
    except Exception as e:
        logger.error(f"Error restoring device {device_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Restore failed: {str(e)}")


@router.post("/devices/backup-all", response_model=MassBackupResponse, summary="Backup all WLED devices")
def backup_all_devices(request: MassBackupRequest):
    """Backup all WLED devices by downloading their config and presets files."""
    logger.info("Starting mass backup for all devices")
    
    devices = get_all_wled_devices()
    if not devices:
        raise HTTPException(status_code=404, detail="No devices found")
    
    logger.info(f"Found {len(devices)} devices for mass backup")
    
    successful_backups = 0
    failed_backups = 0
    
    for device in devices:
        if not device.last_ip:
            logger.warning(f"Device {device.id} has no IP address, skipping")
            failed_backups += 1
            continue
        
        try:
            backup_retriever = WLEDBackupRetriever()
            backup_dir = backup_retriever.backup_device(device.last_ip)
            
            if backup_dir:
                logger.info(f"Successfully backed up device {device.id}")
                successful_backups += 1
            else:
                failed_backups += 1
                
        except Exception as e:
            logger.error(f"Error backing up device {device.id}: {e}")
            failed_backups += 1
    
    if successful_backups == 0:
        raise HTTPException(status_code=500, detail="All device backups failed")

    # Send backup email
    try:
        from api.services.email_service import EmailService
        email_service = EmailService()
        email_success, email_error = email_service.send_backup_email()
        if email_success:
            logger.info("Backup notification email sent successfully")
        else:
            logger.error(f"Failed to send backup notification email: {email_error}")
    except Exception as e:
        logger.error(f"Error sending backup notification email: {e}")
    
    return MassBackupResponse(
        success=True,
        message=f"Mass backup completed: {successful_backups} successful, {failed_backups} failed",
        devices_backed_up=successful_backups,
        total_devices=len(devices),
        failed_backups=failed_backups
    )
