from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
from services.settings_service import get_all_settings, set_all_settings, get_setting, set_setting
from models.dto import AppSettingsDTO, SettingDTO, SuccessResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/settings", response_model=AppSettingsDTO, summary="Get all app settings")
def get_settings():
    """Get all application settings."""
    logger.info("Retrieving all application settings")
    
    settings = get_all_settings()
    logger.debug(f"Retrieved {len(settings)} settings")
    
    return AppSettingsDTO(settings=settings)

@router.post("/settings", response_model=SuccessResponse, summary="Set all app settings")
def update_settings(settings: AppSettingsDTO):
    """Update all application settings."""
    logger.info("Updating all application settings")
    logger.debug(f"New settings: {settings.settings}")
    
    set_all_settings(settings.settings)
    logger.info("Successfully updated all settings")
    
    return SuccessResponse(message="Settings updated successfully")

@router.get("/settings/{key}", response_model=SettingDTO, summary="Get a specific setting")
def get_single_setting(key: str):
    """Get a specific setting by key."""
    logger.info(f"Retrieving setting: {key}")
    
    value = get_setting(key)
    if value is None:
        logger.warning(f"Setting '{key}' not found")
        raise HTTPException(status_code=404, detail=f"Setting '{key}' not found")
    
    logger.debug(f"Setting '{key}' value: {value}")
    return SettingDTO(key=key, value=value)

@router.put("/settings/{key}", response_model=SuccessResponse, summary="Set a specific setting")
def update_single_setting(key: str, setting: SettingDTO):
    """Update a specific setting by key."""
    logger.info(f"Updating setting: {key}")
    logger.debug(f"New value for '{key}': {setting.value}")
    
    set_setting(key, setting.value)
    logger.info(f"Successfully updated setting: {key}")
    
    return SuccessResponse(message=f"Setting '{key}' updated successfully")
