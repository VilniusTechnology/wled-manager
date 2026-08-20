from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Dict, Any
import asyncio
import logging
import requests
import time
from datetime import datetime, timezone

from pydantic import BaseModel
from db.sqlite import (
    update_wled_device_partial, get_all_wled_devices, get_wled_device,
    get_latest_device_info, get_wled_device_by_id, get_connection
)
from models.dto import (
    HealthcheckRequest, HealthcheckResponse, WLEDDeviceDTO, WLEDDeviceUpdateDTO,
    SuccessResponse, DeviceShortInfoDTO, DeviceFullDetailsDTO
)
from api.services.scan_service import process_device
from api.services.device_service import (
    delete_device, add_manual_device, build_device_full_details_dto,
    get_device_and_validate_ip, adopt_devices, release_devices
)
from api.services.wled_health_service import resolve_device_health_status


router = APIRouter()
logger = logging.getLogger(__name__)


@router.delete("/devices/{device_id}")
async def delete_device_endpoint(device_id: str):
    """Delete a device."""
    return delete_device(device_id)

class AddDeviceRequest(BaseModel):
    ip: str
    local_name: str = ""

@router.post("/devices")
async def add_device_endpoint(request: AddDeviceRequest):
    """Manually add a device."""
    return add_manual_device(request.ip, request.local_name)

# Module loaded

class AdoptDeviceRequest(BaseModel):
    device_id: str
    local_device_name: str

class MassHealthcheckRequest(BaseModel):
    ips: List[str]


class ReleaseDeviceRequest(BaseModel):
    device_ids: List[str]


# Device CRUD endpoints
@router.get("/devices", response_model=List[WLEDDeviceDTO], summary="Get all WLED devices")
def get_devices():
    """Get all WLED devices from the database."""
    logger.info("Retrieving all WLED devices from database")
    
    devices = get_all_wled_devices()
    device_list = [WLEDDeviceDTO(**device.dict()) for device in devices]
    
    logger.info(f"Retrieved {len(device_list)} devices from database")
    logger.debug(f"Device MACs: {[device.mac for device in device_list]}")
    
    return device_list

@router.get("/device/short-info", response_model=List[WLEDDeviceDTO], summary="Get all WLED devices (short info)")
def get_devices_short_info():
    """Get all WLED devices from the database (short info endpoint)."""
    logger.info("Retrieving all WLED devices for short-info endpoint")
    
    try:
        devices = get_all_wled_devices()
        logger.info(f"Retrieved {len(devices)} devices from database")
        
        device_list = []
        for device in devices:
            try:
                device_dict = device.dict()
                logger.info(f"Processing device: {device.mac}")
                logger.info(f"Device dict: {device_dict}")
                device_dto = WLEDDeviceDTO(**device_dict)
                device_list.append(device_dto)
            except Exception as e:
                logger.error(f"Error creating DTO for device {device.mac}: {str(e)}")
                logger.exception(e)
        
        logger.info(f"Processed {len(device_list)} devices for short-info endpoint")
        
        return device_list
    except Exception as e:
        logger.error(f"Error in get_devices_short_info: {str(e)}")
        logger.exception(e)
        raise e

@router.get("/devices/{mac}", response_model=WLEDDeviceDTO, summary="Get a specific WLED device by MAC")
def get_device(mac: str):
    """Get a WLED device by MAC address."""
    logger.info(f"Retrieving device with MAC: {mac}")
    
    device = get_wled_device(mac)
    if not device:
        logger.warning(f"Device with MAC {mac} not found")
        raise HTTPException(status_code=404, detail=f"Device with MAC {mac} not found")
    
    logger.debug(f"Device found: {device.name} at IP {device.last_ip}")
    return WLEDDeviceDTO(**device.dict())

@router.get("/devices/{device_id}/details", response_model=DeviceFullDetailsDTO, summary="Get full device details by device ID")
def get_device_details(device_id: str):
    """Get full device details including latest version data by device ID."""
    logger.info(f"Retrieving full details for device ID: {device_id}")
    
    # Get device by device_id
    device = get_wled_device_by_id(device_id)
    if not device:
        logger.warning(f"Device with ID {device_id} not found")
        raise HTTPException(status_code=404, detail=f"Device with ID {device_id} not found")
    
    # Get latest device info from versions table
    latest_info = get_latest_device_info(device.mac)
    
    # Build the full details response
    details = build_device_full_details_dto(device, latest_info)
    
    logger.info(f"Successfully retrieved full details for device: {device.mac}")
    return details



@router.get("/devices/{device_id}/details/refresh", response_model=DeviceFullDetailsDTO, summary="Get full device details by device ID with refresh")
async def get_device_details_refresh(device_id: str, timeout: float = 10.0):
    """Get full device details including latest version data by device ID, with refresh."""
    logger.info(f"Retrieving full details for device ID: {device_id} with refresh")

    device = get_wled_device_by_id(device_id)
    process_result = await process_device(device.last_ip, device.mac, timeout)

    # Re-fetch device to get updated status after process_device
    device = get_wled_device_by_id(device_id)

    # Refresh the device info
    logger.info(f"Refreshing device info for {device_id} at {device.last_ip}")
    
    # Get latest device info 
    # If process_device returned fresh info, use it. 
    # If not, RAISE ERROR instead of falling back to DB for an explicit refresh
    latest_info = None
    if process_result and isinstance(process_result, dict) and process_result.get("device_info"):
        logger.debug(f"Using fresh device info from scan for {device.mac}")
        di = process_result["device_info"]
        latest_info = {
            'cfg': di.get("cfg_full", {}),
            'info': di.get("info_full", {}),
            'state': di.get("state_full", {}),
            'ip': di.get("ip", device.last_ip),
            'timestamp': datetime.now(timezone.utc).isoformat(), # approximate
            'mac': device.mac
        }
    else:
        # User requested a refresh, but we failed to get it. 
        # Do NOT return stale data as it confuses the user (UI looks like it worked but shows old config).
        logger.warning(f"Refresh failed for {device.mac} at {device.last_ip}. Returning 503.")
        raise HTTPException(status_code=503, detail="Failed to refresh configuration from device. Device may be offline or busy.")
    
    # Build the full details response
    details = build_device_full_details_dto(device, latest_info)
    
    logger.info(f"Successfully retrieved full details for device: {device.mac} after refresh")
    return details



@router.put("/devices/{mac}", response_model=WLEDDeviceDTO, summary="Update a WLED device")
def update_device(mac: str, updates: WLEDDeviceUpdateDTO):
    """Update a WLED device by MAC address."""
    logger.info(f"Updating device with MAC: {mac}")
    logger.debug(f"Update data: {updates.dict(exclude_unset=True)}")
    
    device = get_wled_device(mac)
    if not device:
        logger.warning(f"Device with MAC {mac} not found for update")
        raise HTTPException(status_code=404, detail=f"Device with MAC {mac} not found")
    
    # Update the device
    update_dict = updates.dict(exclude_unset=True)
    update_wled_device_partial(update_dict, mac)
    
    # Return updated device
    updated_device = get_wled_device(mac)
    logger.info(f"Successfully updated device: {mac}")
    
    return WLEDDeviceDTO(**updated_device.dict())

@router.post("/devices/adopt", response_model=SuccessResponse, summary="Adopt devices")
def adopt_devices_route(request: List[AdoptDeviceRequest]):
    """Adopt multiple WLED devices by setting adopted to true and local_name."""
    logger.info(f"Adopting {len(request)} devices")
    
    try:
        # Convert Pydantic models to dictionaries
        request_dict = [item.dict() for item in request]
        adopt_devices(request_dict)
        logger.info(f"Successfully adopted {len(request)} devices")
        return SuccessResponse(message=f"Adopted {len(request)} devices")
    except ValueError as e:
        logger.warning(f"ValueError during adoption: {e}")
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/devices/healthcheck", summary="Perform health check on multiple devices")
async def mass_device_healthcheck(request: MassHealthcheckRequest):
    logger.info(f"Performing mass healthcheck for {len(request.ips)} IPs")
    results = {}
    for ip in request.ips:
        is_online, response_time, status, grade, details, error_msg, mac = await resolve_device_health_status(ip)
        results[ip] = {
            "status": status,
            "grade": grade,
            "response_time": response_time,
            "error": error_msg,
            "mac": mac,
            "health_details": details
        }
    return {"success": True, "results": results}


@router.post("/devices/release", response_model=SuccessResponse, summary="Release devices")
def release_devices_route(request: ReleaseDeviceRequest):
    """Release multiple WLED devices by setting adopted to null."""
    logger.info(f"Releasing {len(request.device_ids)} devices")
    
    try:
        release_devices(request.device_ids)
        logger.info(f"Successfully released {len(request.device_ids)} devices")
        return SuccessResponse(message=f"Released {len(request.device_ids)} devices")
    except ValueError as e:
        logger.warning(f"ValueError during release: {e}")
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/scan-refresh", summary="Refresh all known WLED devices by rescanning their IPs")
async def scan_refresh_devices(timeout: float = 10.0):
    """Refresh all devices in the database by rescanning their last known IPs."""
    try:
        logger.info(f"Starting device refresh scan with timeout: {timeout}")
        
        devices = get_all_wled_devices()
        logger.info(f"Found {len(devices)} devices in database to refresh")
        
        refreshed = []
        
        # Create tasks for devices with valid IPs
        valid_devices = [d for d in devices if d.last_ip]
        
        async def refresh_single_device(device):
            try:
                logger.debug(f"+++ Will process refresh for device {device.name} mac:{device.mac} at ip:{device.last_ip}")
                result = await process_device(device.last_ip, device.mac, timeout)
                if result:
                    mac_refreshed = result['mac'] if isinstance(result, dict) and 'mac' in result else result
                    logger.debug(f"Successfully refreshed device {mac_refreshed} at {device.last_ip}")
                    return mac_refreshed
            except Exception as e:
                logger.warning(f"Failed to refresh device {device.mac} at {device.last_ip}: {e}")
            return None

        # Run all refresh tasks concurrently
        tasks = [refresh_single_device(d) for d in valid_devices]
        results = await asyncio.gather(*tasks)
        
        # Filter out None results
        refreshed = [r for r in results if r]
        
        logger.info(f"Refresh scan completed. Updated {len(refreshed)} devices")
        return {"refreshed": refreshed}
    except Exception as e:
        logger.error(f"Error during refresh scan: {e}")
        raise HTTPException(status_code=500, detail=f"Error during refresh scan: {str(e)}")


@router.get("/short-info", response_model=List[DeviceShortInfoDTO], summary="Get short info for all devices")
def get_device_short_info(include_latest: bool = Query(False, description="Include latest configuration and state data")):
    """Get short info for all devices, optimized for UI display."""
    logger.info(f"Retrieving short device info for all devices (include_latest={include_latest})")
    start_time = time.time()
    
    devices = get_all_wled_devices()
    short_info_list = []
    
    # Pre-fetch latest info map if needed
    latest_info_map = {}
    if include_latest:
        from db.sqlite import get_latest_device_info_map
        latest_info_map = get_latest_device_info_map()

    # Pre-fetch backup availability for all devices
    from db.sqlite import get_connection
    backup_status_map = {}
    try:
        with get_connection() as conn:
            # Get count of backups for each device
            cur = conn.execute('SELECT mac, COUNT(*) FROM wled_backups GROUP BY mac')
            for row in cur.fetchall():
                backup_status_map[row[0]] = row[1] > 0
    except Exception as e:
        logger.error(f"Error fetching backup status: {e}")

    for device in devices:
        # Check if device has backups using the pre-fetched map (defaults to False)
        has_backups = backup_status_map.get(device.mac, False)
        try:
            # Check if device has backups using the pre-fetched map (defaults to False)
            has_backups = backup_status_map.get(device.mac, False)
            
            if include_latest:
                # Get latest device info from pre-fetched map
                latest_info = latest_info_map.get(device.mac)
                # We need to modify build_device_short_info_dto to accept has_backups override 
                # OR logic in this loop, but build_device_short_info_dto already calls device_has_backups internally.
                # To optimize, we should refactor build_device_short_info_dto or duplicate minimal logic here.
                # Duplicating minimal logic here is safer to strictly avoid the internal DB call.
                
                # --- Inline optimized DTO construction ---
                short_info = DeviceShortInfoDTO(
                    device_id=device.id,
                    mac=device.mac,
                    name=device.name or device.local_name or device.hostname or device.mac,
                    last_seen=device.last_seen,
                    status=device.status,
                    ip_address=device.last_ip,
                    has_backups=has_backups,
                    discovery_date_time=device.created,
                    id=device.id,
                    last_ip=device.last_ip,
                    local_name=device.local_name,
                    hostname=device.hostname,
                    adopted=device.adopted,
                    usermod_url=device.usermod_url,
                    architecture=device.architecture
                )
                
                # Denormalized fields
                if device.software_version:
                    short_info.software_version = device.software_version
                    short_info.version = device.software_version
                if device.wifi_signal is not None:
                    short_info.signal_strength = device.wifi_signal
                    short_info.signal = str(device.wifi_signal)
                if device.state_on is not None:
                    short_info.state_on = device.state_on
                if device.has_static_ip is not None:
                    short_info.has_static_ip = device.has_static_ip
                if device.wifi_sleep is not None:
                    short_info.wifi_sleep = device.wifi_sleep
                if device.turn_on_after_power_up is not None:
                    short_info.turn_on_after_power_up = device.turn_on_after_power_up
                    
                # Latest info fields
                if latest_info:
                    info = latest_info.get('info', {})
                    state = latest_info.get('state', {})
                    cfg = latest_info.get('cfg', {})
                    
                    if 'ver' in info and not short_info.software_version:
                        short_info.software_version = info['ver']
                        short_info.version = info['ver']
                    if 'wifi' in info and isinstance(info['wifi'], dict) and 'signal' in info['wifi'] and short_info.signal_strength is None:
                        short_info.signal_strength = info['wifi']['signal']
                        short_info.signal = str(info['wifi']['signal'])
                    if 'on' in state and short_info.state_on is None:
                        short_info.state_on = state['on']
                    if cfg and short_info.has_static_ip is None:
                        from utils.wled_config_utils import detect_static_ip_config
                        try:
                            short_info.has_static_ip = detect_static_ip_config(cfg)
                        except Exception:
                            short_info.has_static_ip = None
                    if 'wifi' in cfg and isinstance(cfg['wifi'], dict) and 'sleep' in cfg['wifi'] and short_info.wifi_sleep is None:
                        short_info.wifi_sleep = bool(cfg['wifi']['sleep'])
                    if 'def' in cfg and isinstance(cfg['def'], dict) and 'on' in cfg['def'] and short_info.turn_on_after_power_up is None:
                        short_info.turn_on_after_power_up = bool(cfg['def']['on'])
                        
                    if 'arch' in info and not short_info.architecture:
                        short_info.architecture = info['arch']
                        
                    hw_info = info.get('hw', {})
                    if hw_info:
                        if 'bnd' in hw_info and not short_info.brand:
                            short_info.brand = hw_info['bnd']
                        if 'pm' in hw_info and not short_info.product:
                            short_info.product = hw_info['pm']
                        
                    if latest_info.get('timestamp'):
                        try:
                            short_info.last_seen = datetime.fromisoformat(latest_info['timestamp'])
                        except ValueError:
                            pass
                
            else:
                # Inline optimized construction for basic case
                short_info = DeviceShortInfoDTO(
                    device_id=device.id,
                    mac=device.mac,
                    name=device.name or device.local_name or device.hostname or device.mac,
                    last_seen=device.last_seen,
                    status=device.status,
                    ip_address=device.last_ip,
                    has_backups=has_backups,
                    discovery_date_time=device.created,
                    id=device.id,
                    last_ip=device.last_ip,
                    local_name=device.local_name,
                    hostname=device.hostname,
                    adopted=device.adopted,
                    usermod_url=device.usermod_url,
                    architecture=device.architecture
                )
                # Denormalized fields only
                if device.software_version:
                    short_info.software_version = device.software_version
                    short_info.version = device.software_version
                if device.wifi_signal is not None:
                    short_info.signal_strength = device.wifi_signal
                    short_info.signal = str(device.wifi_signal)
                if device.state_on is not None:
                    short_info.state_on = device.state_on
                if device.has_static_ip is not None:
                    short_info.has_static_ip = device.has_static_ip
                if device.wifi_sleep is not None:
                    short_info.wifi_sleep = device.wifi_sleep
                if device.turn_on_after_power_up is not None:
                    short_info.turn_on_after_power_up = device.turn_on_after_power_up
            
            short_info_list.append(short_info)
            
        except Exception as e:
            logger.error(f"Error processing device {device.mac} for short info: {e}")
            logger.exception(e)
            continue
    
    duration = time.time() - start_time
    logger.info(f"Retrieved short info for {len(short_info_list)} devices in {duration:.4f}s")
    return short_info_list


class ToggleResponse(BaseModel):
    success: bool
    state_on: bool
    message: str

@router.post("/devices/{device_id}/toggle", response_model=ToggleResponse, summary="Toggle WLED device power")
async def toggle_device_power(device_id: str):
    """Toggle the power state of a WLED device."""
    logger.info(f"Toggling power for device: {device_id}")

    device = get_device_and_validate_ip(device_id)

    try:
        import requests
        url = f"http://{device.last_ip}/json/state"
        logger.info(f"Sending toggle command to {url}")

        # Send toggle command {"on": "t"}
        response = requests.post(url, json={"on": "t"}, timeout=5.0)
        response.raise_for_status()

        # Parse response state
        data = response.json()
        # API usually returns full state/info object if successful, or {"success": true} for some older versions
        # But for JSON API POST /json/state, it usually returns {"success":true} unless 'v' is set?
        # Actually WLED JSON API docs say: POSTing to /json/state "Returns the full state object"
        
        new_state = False
        if "on" in data:
            new_state = data["on"]
        elif "state" in data and "on" in data["state"]:
             new_state = data["state"]["on"]
        else:
             # Fallback if state not in response, maybe fetch get_state?
             # But usually response has it.
             # If keys miss, check if we got success:true and assume toggle worked?
             # No, "toggle" means we don't know the new state unless we read it.
             # Let's hope "on" is in the response.
             logger.warning(f"Could not find 'on' state in response: {data.keys()}")
             # If response is just {"success": true}, we might need to GET /json/state
             state_response = requests.get(url, timeout=2.0)
             state_data = state_response.json()
             new_state = state_data.get("on", False)

        logger.info(f"Successfully toggled power for device {device_id}. New state: {new_state}")
        
        # Trigger a background refresh of the device state
        asyncio.create_task(process_device(device.last_ip, device.mac, 5.0))

        return ToggleResponse(success=True, state_on=new_state, message="Device power toggled successfully")

    except requests.exceptions.Timeout:
        logger.error(f"Timeout toggling power for device {device_id}")
        raise HTTPException(status_code=408, detail="Device did not respond within timeout")
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error toggling power for device {device_id}")
        raise HTTPException(status_code=503, detail="Could not connect to device")
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error toggling power for device {device_id}: {e}")
        status_code = e.response.status_code if e.response else 502
        raise HTTPException(status_code=status_code, detail=f"Device rejected request: {status_code}")
    except Exception as e:
        logger.error(f"Failed to toggle power for device {device_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Toggle failed: {str(e)}")

@router.post("/devices/{device_id}/restart", summary="Restart WLED device")
async def restart_device(device_id: str):
    """Restart a WLED device."""
    logger.info(f"Restarting device: {device_id}")

    device = get_device_and_validate_ip(device_id)

    try:
        import requests
        url = f"http://{device.last_ip}/json/state"
        logger.info(f"Sending restart command to {url}")

        # Send restart command {"rb": true}
        response = requests.post(url, json={"rb": True}, timeout=5.0)
        response.raise_for_status()

        logger.info(f"Successfully initiated restart for device {device_id}")
        
        return {"success": True, "message": "Device restart initiated"}

    except requests.exceptions.Timeout:
        logger.error(f"Timeout restarting device {device_id}")
        raise HTTPException(status_code=408, detail="Device did not respond within timeout")
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error restarting device {device_id}")
        raise HTTPException(status_code=503, detail="Could not connect to device")
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error restarting device {device_id}: {e}")
        status_code = e.response.status_code if e.response else 502
        raise HTTPException(status_code=status_code, detail=f"Device rejected request: {status_code}")
    except Exception as e:
        logger.error(f"Failed to restart device {device_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Restart failed: {str(e)}")

@router.post("/devices/{device_id}/healthcheck", summary="Perform device health check")
async def device_healthcheck(device_id: str):
    """Perform an on-demand health check for a device."""
    logger.info(f"Performing health check for device: {device_id}")
    
    device = get_device_and_validate_ip(device_id)
    
    from api.services.device_service import check_and_update_device_status
    
    result = await check_and_update_device_status(device.last_ip, device.mac, device.hostname)
    return result

@router.post("/devices/{device_id}/config", summary="Save device configuration")
async def save_device_config(device_id: str, config: Dict[str, Any] = Body(...)):
    """Save configuration to a WLED device."""
    logger.info(f"Saving configuration for device: {device_id}")
    
    device = get_device_and_validate_ip(device_id)
    
    try:
        import requests
        # Use POST to /json/cfg to update configuration
        # WLED documentation says POST to /json/cfg with JSON body updates config
        url = f"http://{device.last_ip}/json/cfg"
        logger.info(f"Sending configuration to {url}")
        
        # Determine if we should use PUT or POST. 
        # Existing wled_config.py uses PUT. Let's try POST first as it's more standard for file/large JSON uploads in WLED.
        # However, if wled_config.py uses PUT, maybe that's what works for this version?
        # Let's use POST. If it fails (405), we can try PUT.
        
        response = requests.post(url, json=config, timeout=10.0)
        
        # 405 Method Not Allowed logic for fallback (older WLED versions uses PUT)
        if response.status_code == 405:
             logger.info(f"POST failed with 405, trying PUT to {url}")
             response = requests.put(url, json=config, timeout=10.0)
             
        response.raise_for_status()
        
        logger.info(f"Successfully saved configuration for device {device_id}")
        
        # Trigger a refresh to update DB
        asyncio.create_task(process_device(device.last_ip, device.mac, 5.0))
        
        return {"success": True, "message": "Configuration saved successfully"}
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout saving config for device {device_id}")
        raise HTTPException(status_code=408, detail="Device did not respond within timeout")
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error saving config for device {device_id}")
        raise HTTPException(status_code=503, detail="Could not connect to device")
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error saving config for device {device_id}: {e}")
        status_code = e.response.status_code if e.response else 502
        raise HTTPException(status_code=status_code, detail=f"Device rejected request: {status_code}")
    except Exception as e:
        logger.error(f"Failed to save config for device {device_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Save failed: {str(e)}")
