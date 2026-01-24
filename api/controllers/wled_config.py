from fastapi import APIRouter, status, Body
from scanner.wled_retriever import WLEDRetriever
from typing import Any, Dict
import logging
from models.dto import WLEDConfigUpdateRequest, WLEDConfigUpdateResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/wled/config", response_model=WLEDConfigUpdateResponse, summary="Set or update WLED device config")
def set_wled_config(req: WLEDConfigUpdateRequest = Body(...)):
    """
    Set or update the config of a WLED device by IP.
    """
    logger.info(f"Updating WLED config for device at IP: {req.ip}")
    logger.debug(f"Config update timeout: {req.timeout}")
    logger.debug(f"Config keys: {list(req.config.keys()) if req.config else 'None'}")
    
    # Use requests.put directly, as WLEDRetriever does not expose requests
    import requests
    url = f"http://{req.ip}/json/cfg"
    
    try:
        logger.debug(f"Sending PUT request to {url}")
        resp = requests.put(url, json=req.config, timeout=req.timeout)
        resp.raise_for_status()
        
        logger.info(f"Successfully updated config for device at {req.ip}")
        logger.debug(f"Response status: {resp.status_code}")
        
        return WLEDConfigUpdateResponse(success=True, response=resp.json())
    except Exception as e:
        logger.error(f"Failed to update config for device at {req.ip}: {e}")
        return WLEDConfigUpdateResponse(success=False, error=str(e))
