from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple, Union
import logging
import json
import asyncio
import os
import time
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError
import httpx
from fastapi import HTTPException
from db.sqlite import get_wled_device_by_id, update_wled_device_partial, get_wled_device_by_ip, device_has_backups, get_latest_device_info, delete_wled_device
from models.dto import DeviceFullDetailsDTO, DeviceStatus, DeviceShortInfoDTO
from scanner.wled_backup_retriever import WLEDBackupRetriever
from utils.wled_config_utils import detect_static_ip_config
from scanner.wled_scan import retrieve_wled_full_info
from api.services.scan_service import validate_device_mac

logger = logging.getLogger(__name__)

def delete_device(device_id: str):
    """Delete a device by ID."""
    logger.info(f"Deleting device with ID: {device_id}")
    
    device = get_wled_device_by_id(device_id)
    if not device:
        logger.warning(f"Device with ID {device_id} not found")
        raise HTTPException(status_code=404, detail=f"Device with ID {device_id} not found")
    
    success = delete_wled_device(device_id)
    if success:
        logger.info(f"Successfully deleted device {device_id}")
        return {"success": True, "message": f"Device {device_id} deleted successfully"}
    else:
        logger.error(f"Failed to delete device {device_id} from database")
        raise HTTPException(status_code=500, detail="Failed to delete device from database")

def add_manual_device(ip: str, local_name: str):
    """Manually add a WLED device by IP address."""
    logger.info(f"Manually adding device at IP: {ip} with name: {local_name}")
    
    # Verify the device is reachable and is a WLED device
    # We can reuse scan logic or just try to fetch info
    try:
        # Validate IP format first? Optional
        
        # Use existing logic to retrieve full info which saves to DB
        # This function scans, retrieves info, and saves to DB
        device_id = retrieve_wled_full_info(ip)
        
        if device_id:
            logger.info(f"Successfully added/updated device {device_id}")
            
            # If local_name is provided, update it
            if local_name:
                device = get_wled_device_by_id(device_id)
                if device:
                    update_wled_device_partial({'local_name': local_name, 'adopted': True}, device.mac)
            
            return {"success": True, "device_id": device_id, "message": "Device added successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to retrieve device information")
            
    except Exception as e:
        logger.error(f"Failed to add manual device at {ip}: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to add device: {str(e)}")

def adopt_devices(request: List[Dict[str, Any]]):
    """Adopt multiple WLED devices by setting adopted to true and local_name."""
    logger.info(f"Adopting {len(request)} devices")

    for item in request:
        device_id = item.get('device_id')
        local_device_name = item.get('local_device_name')

        logger.debug(f"Adopting device {device_id} with local_name {local_device_name}")

        device = get_wled_device_by_id(device_id)
        if not device:
            logger.warning(f"Device with device_id {device_id} not found")
            raise ValueError(f"Device with device_id {device_id} not found")

        # Update the device with local_name and set adopted to true
        update_dict = {'adopted': True, 'local_name': local_device_name}
        logger.debug(f"Updating adopted device {device.mac} with {update_dict}")
        update_wled_device_partial(update_dict, device.mac)
        
        # Verify the update
        updated_device = get_wled_device_by_id(device_id)
        logger.debug(f"Device after update: {updated_device.dict() if updated_device else 'Not found'}")
        
        logger.debug(f"Successfully adopted device {device_id}")
    
    logger.info(f"Successfully adopted {len(request)} devices")

def release_devices(device_ids: List[str]):
    """Release multiple WLED devices by setting adopted to null."""
    logger.info(f"Releasing {len(device_ids)} devices")

    for device_id in device_ids:
        logger.debug(f"Releasing device {device_id}")

        device = get_wled_device_by_id(device_id)
        if not device:
            logger.warning(f"Device with device_id {device_id} not found")
            raise ValueError(f"Device with device_id {device_id} not found")

        # Update the device
        update_dict = {'adopted': False}
        update_wled_device_partial(update_dict, device.mac)
        
        logger.debug(f"Successfully released device {device_id}")
    
    logger.info(f"Successfully released {len(device_ids)} devices")

def build_device_full_details_dto(device, latest_info=None) -> DeviceFullDetailsDTO:
    """Build a DeviceFullDetailsDTO from a device model and optional latest info."""
    has_backups = device_has_backups(device.mac)
    
    details = DeviceFullDetailsDTO(
        device_id=device.id,
        mac=device.mac,
        name=device.name,
        last_ip=device.last_ip,
        local_name=device.local_name,
        hostname=device.hostname,
        adopted=bool(device.adopted),
        status=device.status,
        last_seen=device.last_seen,
        created=device.created,
        updated=device.updated,
        has_backups=has_backups,
        discovery_date_time=device.created,  # Map created column to discovery_date_time
        usermod_url=device.usermod_url
    )
    
    # Prefer fields from device record if available (denormalized)
    if device.software_version:
        details.software_version = device.software_version
    if device.wifi_signal is not None:
        details.signal_strength = device.wifi_signal
        details.wifi_rssi = device.wifi_signal
    if device.state_on is not None:
        details.state_on = device.state_on
    if device.architecture:
        details.architecture = device.architecture
    if device.led_count is not None:
        details.led_count = device.led_count
    if device.led_count is not None:
        details.led_count = device.led_count
    if device.has_static_ip is not None:
        details.has_static_ip = device.has_static_ip
    if device.wifi_sleep is not None:
        details.wifi_sleep = device.wifi_sleep
    if device.turn_on_after_power_up is not None:
        details.turn_on_after_power_up = device.turn_on_after_power_up

    # If we have latest info, extract and overwrite/set the detailed fields
    if latest_info:
        details.latest_info = latest_info.get('info', {})
        details.latest_state = latest_info.get('state', {})
        details.latest_config = latest_info.get('cfg', {})
        
        # Convert timestamp string to datetime if available
        if latest_info.get('timestamp'):
            try:
                details.latest_timestamp = datetime.fromisoformat(latest_info['timestamp'])
            except ValueError:
                logger.warning(f"Could not parse timestamp: {latest_info['timestamp']}")
        
        # Extract commonly used fields for convenience (fallback or if not in device record)
        info = latest_info.get('info', {})
        state = latest_info.get('state', {})
        cfg = latest_info.get('cfg', {})
        
        # Software version from info.ver
        if 'ver' in info and not details.software_version:
            details.software_version = info['ver']
        
        # Signal strength from info.wifi.signal
        if 'wifi' in info and isinstance(info['wifi'], dict) and 'signal' in info['wifi'] and details.signal_strength is None:
            details.signal_strength = info['wifi']['signal']
            details.wifi_rssi = info['wifi']['signal']
        
        # WiFi channel from info.wifi.channel
        if 'wifi' in info and isinstance(info['wifi'], dict) and 'channel' in info['wifi']:
            details.wifi_channel = info['wifi']['channel']
        
        # State information
        if 'on' in state and details.state_on is None:
            details.state_on = state['on']
        
        if 'bri' in state:
            details.brightness = state['bri']
        
        if 'ps' in state:
            details.current_preset = state['ps']
        
        # Device hardware info
        if 'leds' in info and isinstance(info['leds'], dict) and 'count' in info['leds'] and details.led_count is None:
            details.led_count = info['leds']['count']
        
        if 'uptime' in info:
            details.uptime = info['uptime']
        
        if 'freeheap' in info:
            details.free_heap = info['freeheap']
        
        if 'arch' in info and not details.architecture:
            details.architecture = info['arch']
        
        # Detect static IP configuration from config
        if cfg and details.has_static_ip is None:
            try:
                details.has_static_ip = detect_static_ip_config(cfg)
            except Exception as e:
                logger.warning(f"Error detecting static IP config for device {device.mac}: {e}")
                details.has_static_ip = None
        
        # WiFi Sleep
        if 'wifi' in cfg and isinstance(cfg['wifi'], dict) and 'sleep' in cfg['wifi'] and details.wifi_sleep is None:
            details.wifi_sleep = bool(cfg['wifi']['sleep'])
        if 'def' in cfg and isinstance(cfg['def'], dict) and 'on' in cfg['def'] and details.turn_on_after_power_up is None:
            details.turn_on_after_power_up = bool(cfg['def']['on'])
    
    return details

def build_device_short_info_dto(device, latest_info=None) -> DeviceShortInfoDTO:
    """Build a DeviceShortInfoDTO from a device model and optional latest info."""
    has_backups = device_has_backups(device.mac)
    
    short_info = DeviceShortInfoDTO(
        device_id=device.id,
        mac=device.mac,
        name=device.name or device.local_name or device.hostname or device.mac,
        last_seen=device.last_seen,
        status=device.status,
        ip_address=device.last_ip,
        has_backups=has_backups,
        discovery_date_time=device.created,  # Map created column to discovery_date_time
        # Keep old fields for compatibility
        id=device.id,
        last_ip=device.last_ip,
        local_name=device.local_name,
        hostname=device.hostname,
        adopted=device.adopted,
        usermod_url=device.usermod_url
    )
    
    # Use fields from device record if available (denormalized)
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

    # If we have latest info, extract and set additional fields (as fallback or supplement)
    if latest_info:
        info = latest_info.get('info', {})
        state = latest_info.get('state', {})
        cfg = latest_info.get('cfg', {})
        
        # Software version from info.ver
        if 'ver' in info and not short_info.software_version:
            short_info.software_version = info['ver']
            short_info.version = info['ver']  # compatibility field
        
        # Signal strength from info.wifi.signal
        if 'wifi' in info and isinstance(info['wifi'], dict) and 'signal' in info['wifi'] and short_info.signal_strength is None:
            short_info.signal_strength = info['wifi']['signal']
            short_info.signal = str(info['wifi']['signal'])  # compatibility field
        
        # State information
        if 'on' in state and short_info.state_on is None:
            short_info.state_on = state['on']
        
        # Detect static IP configuration from config
        if cfg and short_info.has_static_ip is None:
            try:
                short_info.has_static_ip = detect_static_ip_config(cfg)
            except Exception as e:
                logger.warning(f"Error detecting static IP config for device {device.mac}: {e}")
                short_info.has_static_ip = None
        
        # WiFi Sleep
        if 'wifi' in cfg and isinstance(cfg['wifi'], dict) and 'sleep' in cfg['wifi'] and short_info.wifi_sleep is None:
            short_info.wifi_sleep = bool(cfg['wifi']['sleep'])
        if 'def' in cfg and isinstance(cfg['def'], dict) and 'on' in cfg['def'] and short_info.turn_on_after_power_up is None:
            short_info.turn_on_after_power_up = bool(cfg['def']['on'])
        
        # Set last seen from latest timestamp
        if latest_info.get('timestamp'):
            try:
                short_info.last_seen = datetime.fromisoformat(latest_info['timestamp'])
                short_info.lastSeen = latest_info['timestamp']  # compatibility field
            except ValueError:
                logger.warning(f"Could not parse timestamp: {latest_info['timestamp']}")
    
    return short_info
    
    return short_info

def get_device_and_validate_ip(device_id: str):
    """Get a device by ID and validate it has an IP address."""
    device = get_wled_device_by_id(device_id)
    if not device:
        logger.warning(f"Device with ID {device_id} not found")
        raise HTTPException(status_code=404, detail=f"Device with ID {device_id} not found")
    
    if not device.last_ip:
        logger.warning(f"Device {device_id} has no IP address")
        raise HTTPException(status_code=400, detail="Device has no IP address")
    
    return device



async def upload_file_to_device(ip_address: str, file_path: str, filename: str):
    """Upload a file to a WLED device using settings/sec page approach."""
    logger.info(f"Starting settings/sec upload of {filename} to {ip_address}")
    logger.debug(f"File path: {file_path}")
    
    try:
        # Verify file exists and is readable
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} does not exist")
        
        logger.debug(f"File size: {os.path.getsize(file_path)} bytes")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Step 1: Go to settings/sec page
            settings_url = f"http://{ip_address}/settings/sec"
            logger.debug(f"Step 1: Opening settings/sec page: {settings_url}")
            
            settings_response = await client.get(settings_url)
            settings_response.raise_for_status()
            logger.debug(f"Settings/sec page response status: {settings_response.status_code}")
            
            # Step 2: Read file content
            logger.debug(f"Step 2: Reading file content for {filename}")
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            files = {
                'data': (filename, file_content, 'application/octet-stream')
            }
            
            logger.debug(f"Uploading {filename} with content length: {len(file_content)}")
            
            # Step 3: Submit the form to /upload endpoint
            upload_url = f"http://{ip_address}/upload"
            logger.debug(f"Step 3: Posting form to upload endpoint: {upload_url}")
            
            try:
                upload_response = await client.post(upload_url, files=files)
                logger.debug(f"Upload response status: {upload_response.status_code}")
                logger.debug(f"Upload response text: {upload_response.text[:200]}")
                
                # Wait for 200 response before returning and logging success
                if upload_response.status_code != 200:
                    logger.error(f"Upload failed with status {upload_response.status_code}: {upload_response.text}")
                    raise HTTPException(status_code=502, detail=f"Device returned status {upload_response.status_code}: {upload_response.text}")
                
                upload_response.raise_for_status()
                
            except httpx.ReadError as e:
                # Handle ReadError(BrokenResourceError()) - device may restart after upload, treat as success
                logger.info(f"Device connection broken during response (likely device restart after upload) - treating as success: {e}")
            except httpx.RemoteProtocolError as e:
                # Handle other protocol errors that may indicate successful upload with device restart
                logger.info(f"Protocol error during response (likely device restart after upload) - treating as success: {e}")
            except Exception as upload_ex:
                # Re-raise other exceptions that aren't related to device restart
                raise upload_ex

        logger.info(f"Successfully uploaded {filename} to {ip_address} using settings/sec approach")
        
    except httpx.TimeoutException as e:
        logger.error(f"Upload timeout for {filename} to {ip_address}: {e}")
        raise HTTPException(status_code=408, detail=f"Upload timeout: device at {ip_address} did not respond within 30 seconds")
    except httpx.ConnectError as e:
        logger.error(f"Connection error uploading {filename} to {ip_address}: {e}")
        raise HTTPException(status_code=503, detail=f"Could not connect to device at {ip_address}")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error uploading {filename} to {ip_address}: {e}")
        raise HTTPException(status_code=502, detail=f"Device rejected upload: {e.response.status_code} - {e.response.text}")
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:
        logger.error(f"Invalid file type: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to upload {filename} to {ip_address}: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

async def perform_ota_update(ip_address: str, firmware_file_path: str, filename: str, device_architecture: str = None):
    """Perform OTA firmware update on a WLED device using the /update endpoint."""
    import time
    start_time = time.time()

    logger.info(f"🚀 Starting OTA update of {filename} to {ip_address}")
    logger.info(f"📁 Firmware file path: {firmware_file_path}")

    steps_completed = []
    warnings = []

    try:
        # Step 1: Validate firmware compatibility
        logger.info("🔍 Step 1: Validating firmware compatibility...")
        
        # Check if filename indicates architecture
        firmware_arch = None
        if "ESP8266" in filename.upper():
            firmware_arch = "esp8266"
        elif "ESP32" in filename.upper():
            firmware_arch = "esp32"
        
        if firmware_arch and device_architecture:
            if firmware_arch.lower() != device_architecture.lower():
                error_msg = f"❌ Firmware architecture mismatch! Firmware is for {firmware_arch.upper()} but device is {device_architecture.upper()}"
                logger.error(error_msg)
                raise HTTPException(
                    status_code=400, 
                    detail=f"Firmware type mismatch. Device architecture: {device_architecture}, Firmware type: {firmware_arch}"
                )
        
        if firmware_arch and device_architecture:
            logger.info(f"✅ Architecture validation passed: Device ({device_architecture}) matches firmware ({firmware_arch})")
        elif firmware_arch:
            logger.warning(f"⚠️  Firmware appears to be for {firmware_arch.upper()} but device architecture unknown")
            warnings.append(f"Firmware type detected as {firmware_arch.upper()} but device architecture not confirmed")
        else:
            logger.warning("⚠️  Could not determine firmware architecture from filename")
            warnings.append("Could not determine firmware architecture from filename")
        
        steps_completed.append("Firmware compatibility validated")

        # Step 2: Verify file exists and is readable
        logger.info("🔍 Step 2: Verifying firmware file...")
        if not os.path.exists(firmware_file_path):
            raise FileNotFoundError(f"Firmware file {firmware_file_path} does not exist")

        file_size = os.path.getsize(firmware_file_path)
        logger.info(f"✅ File verification complete. Size: {file_size} bytes ({file_size / 1024 / 1024:.2f} MB)")
        steps_completed.append("File verification")

        # Check if file size is reasonable for firmware (typically 1-2MB)
        if file_size > 5 * 1024 * 1024:  # 5MB limit
            raise ValueError(f"Firmware file too large: {file_size} bytes. Maximum allowed is 5MB.")

        # Step 3: Initialize HTTP client
        logger.info("🌐 Step 3: Initializing connection to device...")
        async with httpx.AsyncClient(timeout=300.0) as client:  # 5 minute timeout for OTA
            steps_completed.append("HTTP client initialized")

            # Step 4: Read firmware file content
            logger.info("📖 Step 4: Reading firmware file content...")
            with open(firmware_file_path, 'rb') as f:
                firmware_content = f.read()

            logger.info(f"✅ Firmware content loaded. Size: {len(firmware_content)} bytes")
            steps_completed.append("Firmware content loaded")

            # Step 5: Prepare multipart form data
            logger.info("📦 Step 5: Preparing firmware upload data...")
            files = {
                'update': (filename, firmware_content, 'application/octet-stream')
            }
            logger.info(f"✅ Upload data prepared for file: {filename}")
            steps_completed.append("Upload data prepared")

            # Step 6: Send firmware to /update endpoint
            update_url = f"http://{ip_address}/update"
            logger.info(f"📤 Step 6: Sending firmware to device at {update_url}...")
            logger.info(f"⏳ This may take several minutes depending on file size and device...")

            upload_start = time.time()
            response = await client.post(update_url, files=files)
            upload_duration = time.time() - upload_start

            logger.info(f"📡 Device responded with status: {response.status_code}")
            logger.info(f"⏱️  Upload completed in {upload_duration:.2f} seconds")
            steps_completed.append(f"Firmware upload completed in {upload_duration:.2f}s")

            # Log response details
            response_text = response.text[:1000]  # Limit log size
            if len(response.text) > 1000:
                response_text += "... (truncated)"
            logger.info(f"📄 Device response: {response_text}")

            # Step 7: Analyze device response
            logger.info("🔍 Step 7: Analyzing device response...")
            if response.status_code == 200:
                logger.info("✅ OTA update request ACCEPTED by device!")
                logger.info("🔄 Device will now restart and apply the firmware update...")
                logger.info("⚠️  Note: Device connection may be lost during restart")

                steps_completed.append("OTA update accepted by device")
                warnings.append("Device will restart automatically - connection may be lost")

                total_duration = time.time() - start_time
                logger.info(f"🎉 OTA update process completed successfully in {total_duration:.2f} seconds")

                return {
                    "success": True,
                    "message": "OTA update initiated successfully. Device will restart and apply firmware.",
                    "device_ip": ip_address,
                    "firmware_filename": filename,
                    "firmware_size": file_size,
                    "upload_duration": upload_duration,
                    "device_response_status": response.status_code,
                    "device_response_text": response.text,
                    "steps_completed": steps_completed,
                    "warnings": warnings,
                    "total_duration": total_duration
                }
            else:
                logger.error(f"❌ OTA update FAILED with status {response.status_code}")
                logger.error(f"❌ Device response: {response.text}")

                steps_completed.append(f"OTA update failed (HTTP {response.status_code})")

                raise HTTPException(
                    status_code=502,
                    detail=f"Device rejected OTA update: {response.status_code} - {response.text}"
                )

    except httpx.TimeoutException as e:
        logger.error(f"⏰ OTA update TIMEOUT for {filename} to {ip_address}: {e}")
        steps_completed.append("OTA update timed out")
        raise HTTPException(
            status_code=408,
            detail=f"OTA update timeout: device at {ip_address} did not respond within 5 minutes. This may indicate the device restarted successfully."
        )
    except httpx.ConnectError as e:
        logger.error(f"🔌 Connection error during OTA update {filename} to {ip_address}: {e}")
        steps_completed.append("Connection failed")
        raise HTTPException(
            status_code=503,
            detail=f"Could not connect to device at {ip_address}. Device may have restarted after successful update."
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"🌐 HTTP error during OTA update {filename} to {ip_address}: {e}")
        steps_completed.append(f"HTTP error (status {e.response.status_code})")
        raise HTTPException(
            status_code=502,
            detail=f"Device rejected OTA update: {e.response.status_code} - {e.response.text}"
        )
    except FileNotFoundError as e:
        logger.error(f"📁 Firmware file not found: {e}")
        steps_completed.append("Firmware file not found")
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        logger.error(f"❌ Invalid firmware file: {e}")
        steps_completed.append("Invalid firmware file")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"💥 Failed to perform OTA update {filename} to {ip_address}: {e}")
        steps_completed.append("Unexpected error occurred")
        raise HTTPException(status_code=500, detail=f"OTA update failed: {str(e)}")

async def check_and_update_device_status(ip: str, mac: str = None, hostname: str = None) -> Dict[str, Any]:
    """
    Check a device's health status by IP and update its status in the database.
    Returns a dict with status info.
    
    When a MAC is provided, this function also verifies that the device at the IP
    actually has that MAC address. If the MAC doesn't match (IP reassigned to 
    different device), the original device is marked as offline.
    
    If the stored IP is not reachable, attempts to resolve the new IP using:
    1. ARP cache lookup
    2. mDNS hostname resolution  
    3. Network scan with MAC matching
    """
    import datetime
    from datetime import timezone
    logger = logging.getLogger(__name__)
    logger.debug(f"Checking health status for device at {ip} (MAC: {mac}, hostname: {hostname})")
    
    from api.services.wled_health_service import resolve_device_health_status
    
    current_ip = ip
    
    # 1. Health Check first
    is_online, response_time, status, grade, details, error_msg, discovered_mac = await resolve_device_health_status(current_ip, timeout=5.0, expected_mac=mac)

    # 2. If TCP ping fails and we have a MAC, attempt IP resolution
    if not is_online and mac:
        if error_msg and "IP reassigned" in error_msg:
             logger.info(f"Stored IP {ip} reassigned, attempting IP resolution for MAC {mac}...")
        else:
             logger.info(f"Stored IP {ip} offline for MAC {mac}, attempting IP resolution...")
        try:
            from utils.ip_resolver import resolve_device_ip
            from services.settings_service import get_setting
            from scanner.wled_scan import get_local_ip
            import ipaddress
            
            network_cidr = get_setting("network_range")
            if not network_cidr:
                local_ip = get_local_ip()
                network = ipaddress.IPv4Network(local_ip + '/24', strict=False)
                network_cidr = str(network)
            
            resolved_ip = await asyncio.to_thread(
                resolve_device_ip, 
                mac, 
                hostname, 
                network_cidr
            )
            
            if resolved_ip and resolved_ip != ip:
                logger.info(f"Resolved new IP {resolved_ip} for MAC {mac} (was {ip})")
                from db.sqlite import update_wled_device_partial
                await asyncio.to_thread(update_wled_device_partial, {'last_ip': resolved_ip}, mac)
                
                current_ip = resolved_ip
                # Re-check health on new IP
                is_online, response_time, status, grade, details, error_msg, discovered_mac = await resolve_device_health_status(current_ip, timeout=5.0, expected_mac=mac)
        except Exception as e:
            logger.warning(f"IP resolution failed for {mac}: {e}")

    target_mac = mac or discovered_mac

    result = {
        "ip": current_ip,
        "status": status,
        "grade": grade,
        "response_time": response_time,
        "last_seen": datetime.datetime.now(timezone.utc).isoformat(),
        "error_message": error_msg,
        "mac": target_mac,
        "health_details": details
    }
    
    if target_mac:
        from db.sqlite import update_wled_device_partial
        logger.info(f"Updating status for {target_mac} (IP: {current_ip}): status={result['status']}, grade={result['grade']}")
        
        updates = {
            "status": result["status"],
            "last_seen": result["last_seen"],
        }
        
        # Store wifi signal if available
        if "signal_dbm" in details:
            updates["wifi_signal"] = details["signal_dbm"]
        elif "signal_pct" in details:
            updates["wifi_signal"] = details["signal_pct"]
            
        await asyncio.to_thread(update_wled_device_partial, updates, target_mac)
    else:
        logger.warning(f"Could not update status in DB for {current_ip} because MAC is unknown")
    
    return result
