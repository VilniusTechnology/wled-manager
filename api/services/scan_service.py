
import ipaddress
import asyncio
import datetime
from datetime import timezone
import json
import hashlib
import logging
from typing import Dict, Any, Optional
from db.models import WLEDDevice, WLEDDeviceVersion
from db.sqlite import upsert_device_config, insert_device_version, get_wled_device, insert_or_update_wled_device, update_wled_device_partial, get_latest_device_info
from db.convert import dto_to_db_model
from scanner.wled_scan import get_local_ip, scan_network, retrieve_wled_full_info
from scanner.wled_backup_retriever import WLEDBackupRetriever
from services.settings_service import get_setting
from utils.wled_config_utils import detect_static_ip_config

logger = logging.getLogger(__name__)


async def create_backup_and_version_records(
    ip: str,
    retrieved_mac: str,
    deviceInfo: Dict[str, Any],
    cfg_full: Dict[str, Any],
    info_full: Dict[str, Any],
    state_full: Dict[str, Any]
) -> None:
    """
    Create backup and version records for a WLED device.
    
    Args:
        ip: Device IP address
        retrieved_mac: Device MAC address
        deviceInfo: Complete device information dictionary
        cfg_full: Device configuration dictionary
        info_full: Device info dictionary
        state_full: Device state dictionary
    """
    # Check if configuration has actually changed
    latest_info = get_latest_device_info(retrieved_mac)
    
    # Calculate hash of current config
    current_cfg_str = json.dumps(cfg_full, sort_keys=True)
    current_cfg_hash = hashlib.md5(current_cfg_str.encode()).hexdigest()
    
    has_changes = True
    if latest_info:
        last_cfg = latest_info.get('cfg', {})
        last_cfg_str = json.dumps(last_cfg, sort_keys=True)
        last_cfg_hash = hashlib.md5(last_cfg_str.encode()).hexdigest()
        
        if current_cfg_hash == last_cfg_hash:
            logger.debug(f"Device {retrieved_mac} configuration has not changed (hash match). Skipping backup and version creation.")
            has_changes = False
    
    if not has_changes:
        return

    logger.info(f"Device {retrieved_mac} has changes, creating backup and version records")
    
    # Create backup
    logger.debug("Creating device backup")
    backup_retriever = WLEDBackupRetriever()
    backup_retriever.backup_device(ip)
    
    # Convert to DB model for configs
    db_model = dto_to_db_model(
        mac=retrieved_mac,
        mac_original=deviceInfo.get("info_full", {}).get("wifi", {}).get("bssid", ""),
        ip=deviceInfo.get("ip", ip),
        cfg_full=cfg_full,
        info_full=info_full,
        state_full=state_full
    )
    
    logger.debug("Upserting device configuration")
    upsert_device_config(db_model)
    logger.debug("Device configuration upserted successfully")
    
    # Create version record
    logger.debug("Creating new version record")
    device_version = WLEDDeviceVersion(
        mac=retrieved_mac,
        ip=deviceInfo.get("ip", ip),
        mqtt=json.dumps(deviceInfo.get("mqtt")),
        network=json.dumps(deviceInfo.get("network")),
        cfg_full=json.dumps(cfg_full),
        info_full=json.dumps(info_full),
        state_full=json.dumps(state_full),
        device_id=hashlib.md5(retrieved_mac.encode()).hexdigest()
    )
    insert_device_version(device_version)
    logger.debug("Version record created successfully")

# ==============================================================================
# DEVICE FIELD MAPPING CONFIGURATION
# ==============================================================================
# IMPORTANT: When adding new fields to the wled_devices database table,
# you MUST add them to this mapping to ensure they are extracted from the WLED 
# JSON responses and saved to the database. If you forget to add them here,
# the database will contain stale/missing data, causing bugs in UI and filters!
# 
# Format: "db_column_name": ("root_key", ("path", "to", "field"), type_cast_function)
# ==============================================================================
WLED_DB_FIELD_MAPPING = {
    "software_version": ("info_full", ("ver",), str),
    "wifi_signal": ("info_full", ("wifi", "signal"), int),
    "state_on": ("state_full", ("on",), bool),
    "architecture": ("info_full", ("arch",), str),
    "led_count": ("info_full", ("leds", "count"), int),
    "wifi_sleep": ("cfg_full", ("wifi", "sleep"), bool),
}

def extract_device_details(info: Dict[str, Any]) -> Dict[str, Any]:
    """Extract denormalized fields from device info using the automated mapping."""
    details = {}
    
    # 1. Automated Extraction via Mapping
    for db_field, (root_key, path, type_cast) in WLED_DB_FIELD_MAPPING.items():
        try:
            current_level = info.get(root_key, {})
            # Traverse the nested path
            for key in path:
                if isinstance(current_level, dict) and key in current_level:
                    current_level = current_level[key]
                else:
                    # Path not found
                    current_level = None
                    break
            
            # Apply type casting if value was found
            if current_level is not None:
                details[db_field] = type_cast(current_level)
        except (ValueError, TypeError) as e:
            logger.warning(f"Error casting field {db_field} to {type_cast.__name__}: {e}")

    # 2. Complex/Custom Extractions
    # Static IP requires evaluating multiple fields to determine status
    try:
        details['has_static_ip'] = detect_static_ip_config(info.get("cfg_full", {}))
    except Exception:
        pass
        
    return details


def validate_device_mac(retrieved_mac: str, stored_mac: str) -> bool:
    """
    Validate that the MAC address from the device matches the stored MAC.
    Returns True if MAC addresses match, False otherwise.
    """
    if not retrieved_mac or not stored_mac:
        return False
        
    # Normalize MAC addresses for comparison (remove colons and convert to lowercase)
    retrieved_mac = retrieved_mac.lower().replace(':', '')
    stored_mac = stored_mac.lower().replace(':', '')
    
    return retrieved_mac == stored_mac

async def process_existing_device(mac: str, info: Dict[str, Any], existing_device: WLEDDevice, ip: str) -> bool:
    """
    Process an existing WLED device, update its information if needed.
    Returns True if device was changed and needs backup, False otherwise.
    """
    # Device exists and MAC matches, check for changes
    updates_needed = {}

    # Get current device info
    current_ip = info.get("ip", ip)
    current_name = info.get("info_full", {}).get("name")
    current_version = info.get("info_full", {}).get("version", "unknown")
    
    # Extract mDNS hostname from config if available
    # The structure is cfg_full -> id -> mdns
    cfg_full = info.get("cfg_full", {})
    current_hostname = cfg_full.get("id", {}).get("mdns")
    
    # Fallback to name if mDNS is not set (though it usually is for WLED)
    if not current_hostname:
        current_hostname = current_name
    
    # Extract extra details
    extra_details = extract_device_details(info)
    updates_needed.update(extra_details)
    
    logger.debug(f"Current device info: IP={current_ip}, Name={current_name}, Hostname={current_hostname}, Version={current_version}")
    
    if existing_device.last_ip != current_ip:
        logger.debug(f"IP changed: {existing_device.last_ip} -> {current_ip}")
        updates_needed['last_ip'] = current_ip
    
    if existing_device.local_name != current_name:
        logger.debug(f"Local name changed: {existing_device.local_name} -> {current_name}")
        updates_needed['local_name'] = current_name
    
    if existing_device.hostname != current_hostname:
        logger.debug(f"Hostname changed: {existing_device.hostname} -> {current_hostname}")
        updates_needed['hostname'] = current_hostname
    
    if existing_device.name != current_name:
        logger.debug(f"Name changed: {existing_device.name} -> {current_name}")
        updates_needed['name'] = current_name
    
    # Update last_seen - we successfully retrieved info from the device
    current_time = datetime.datetime.utcnow()
    updates_needed['last_seen'] = current_time
    # Note: status will be updated by the health check that runs after this
    logger.debug(f"Updating process_existing_device last_seen to {current_time}")
    
    # Update only changed fields
    if updates_needed:
        logger.debug(f"Updating process_existing_device device {mac} with changes: {updates_needed}")
        update_wled_device_partial(updates_needed, mac)
        logger.debug(f"Device {existing_device.name} mac: {mac} update completed successfully")

    return True

async def process_new_device(mac: str, info: Dict[str, Any], ip: str) -> None:
    """
    Process a newly discovered WLED device and add it to the database.
    """
    # Extract mDNS hostname from config if available
    cfg_full = info.get("cfg_full", {})
    hostname = cfg_full.get("id", {}).get("mdns")
    name = info.get("info_full", {}).get("name")
    
    # Fallback to name if mDNS is not set
    if not hostname:
        hostname = name

    # Extract extra details
    extra_details = extract_device_details(info)

    # New device
    device_data = WLEDDevice(
        mac=mac,
        last_ip=info.get("ip", ip),
        local_name=name,
        hostname=hostname,
        name=name,
        adopted=False,
        last_seen=datetime.datetime.utcnow(),
        status='unknown',  # Status will be set by health check after insertion
        **extra_details
    )
    # Insert/update the device first
    insert_or_update_wled_device(device_data)

async def process_device(ip: str, existingMac: Optional[str] = None, timeout=10.0):
    logger.info(f"process_device: {ip}")
    """Process a single WLED device: fetch info, update DB, create backups if changed."""

    try:
        logger.debug(f"~~~ Fetching WLED device info from IP: {ip}")
        loop = asyncio.get_running_loop()
        deviceInfo = await loop.run_in_executor(None, retrieve_wled_full_info, ip, timeout)
        retrieved_mac = deviceInfo.get('mac')

        if not deviceInfo:
            logger.debug(f"No info returned from device at {ip}")
            return None

        if not isinstance(deviceInfo, dict):
            logger.debug(f"Invalid info format from {ip}: {type(deviceInfo)}")
            return None

        if "error" in deviceInfo:
            logger.error(f"Error in device response from {ip}/json/info: {deviceInfo['error']}. {deviceInfo}")
            
            # Auto-healing: Try to resolve IP if we have the MAC and connection failed
            target_mac = existingMac or deviceInfo.get("mac")
            if target_mac:
                logger.info(f"Connection failed to {ip} for MAC {target_mac}. Attempting to resolve new IP...")
                try:
                    from utils.ip_resolver import resolve_device_ip
                    # Get network range
                    network_cidr = get_setting("network_range")
                    if not network_cidr:
                        local_ip = get_local_ip()
                        network = ipaddress.IPv4Network(local_ip + '/24', strict=False)
                        network_cidr = str(network)

                    # Retrieve hostname if possible (from DB)
                    hostname = None
                    if target_mac and not hostname:
                         # Try to fetch device to get hostname if we don't have it
                         stored_device = get_wled_device(target_mac)
                         if stored_device:
                             hostname = stored_device.hostname

                    # Run IP resolution in thread
                    resolved_ip = await asyncio.to_thread(
                        resolve_device_ip, 
                        target_mac, 
                        hostname, 
                        network_cidr
                    )

                    if resolved_ip and resolved_ip != ip:
                         logger.info(f"Resolved new IP {resolved_ip} for MAC {target_mac}. Updating DB and retrying...")
                         # Update DB
                         update_wled_device_partial({'last_ip': resolved_ip}, target_mac)
                         
                         # Retry fetch with new IP
                         ip = resolved_ip
                         deviceInfo = await loop.run_in_executor(None, retrieve_wled_full_info, ip, timeout)
                         retrieved_mac = deviceInfo.get('mac')
                         
                         if "error" not in deviceInfo and retrieved_mac:
                             logger.info(f"Retry successful for {target_mac} at {resolved_ip}")
                         else:
                             # Retry failed too
                             logger.warning(f"Retry failed for {target_mac} at {resolved_ip}: {deviceInfo.get('error')}")
                    else:
                        logger.warning(f"Could not resolve new IP for MAC {target_mac}")

                except Exception as resolve_err:
                    logger.error(f"Error during IP resolution for {target_mac}: {resolve_err}")

            # If still failed (or resolution didn't help), mark offline
            if "error" in deviceInfo:
                 if target_mac:
                    update_wled_device_partial({'status': 'offline'}, target_mac)
                    logger.debug(f"Marked device {target_mac} as offline due to error")
                 return None
        
        if not retrieved_mac:
            logger.debug(f"No MAC address in device response from {ip}, existing mac: {existingMac}")
            if existingMac:
                update_wled_device_partial({'status': 'offline'}, existingMac)
                logger.debug(f"Marked device {existingMac} as offline due to missing MAC")
            return None
            
        # Normalize the configuration values before processing
        from utils.wled_normalizer import normalize_sync_recv_values
        if "cfg_full" in deviceInfo:
            deviceInfo["cfg_full"] = normalize_sync_recv_values(deviceInfo["cfg_full"])

        # Convert to DB model for configs
        cfg_full = deviceInfo.get("cfg_full", {})
        info_full = deviceInfo.get("info_full", {})
        state_full = deviceInfo.get("state_full", {})

        # Validate and normalize sync configuration
        from utils.config_validators import validate_sync_config
        cfg_full = validate_sync_config(cfg_full)
        
        # Check if device exists in wled_devices table
        existing_device = get_wled_device(retrieved_mac)
        if existing_device:
            mac = existing_device.mac
            logger.debug(f"!!! Device info from {ip}: ID=name={existing_device.id}, name={existing_device.name}, existing MAC={existing_device.mac}, retrieved MAC={retrieved_mac}")

            if existingMac and not validate_device_mac(retrieved_mac, existingMac):
                logger.warning(f"*** !!!!!!!!!!!!! ~ ~ ~ ~ ~ !!!!!!!!!!!!! *** MAC address mismatch for IP {ip}. DEVICE IP HAD CHANGED. Expected {existingMac} vs {retrieved_mac}, Marking it as OFFLINE.")
                update_wled_device_partial({'status': 'offline'}, existingMac)
                return { "mac": existingMac, "device_info": None }

            logger.debug(f"!!! existingMac: {existingMac}, retrieved_mac: {retrieved_mac}")

            # if not existingMac and validate_device_mac(existingMac, retrieved_mac):

            logger.debug(f"!!! Will process existing device: MAC={existing_device.mac}, Last IP={existing_device.last_ip}, Status={existing_device.status}")
            await process_existing_device(existing_device.mac, deviceInfo, existing_device, ip)


        if not existing_device:
            logger.debug(f"!!! Device at {ip} is new, retrieved MAC={retrieved_mac}")
            mac = retrieved_mac
            await process_new_device(retrieved_mac, deviceInfo, ip)

        try:
            from api.services.device_service import check_and_update_device_status
            fresh_device = get_wled_device(retrieved_mac)
            if fresh_device and fresh_device.last_ip:
                # Use check_and_update_device_status which verifies MAC before setting status
                # This prevents marking a device as online if its IP was reassigned to a different device
                result = await check_and_update_device_status(fresh_device.last_ip, fresh_device.mac, fresh_device.hostname)
                logger.debug(f"Initial health check for device {mac}: {result.get('status')} (grade {result.get('grade')})")
            else:
                logger.warning(f"Cannot perform health check for device {mac}: no IP address available")
        except Exception as e:
            logger.warning(f"Failed to perform health check for device {mac}: {e}")

        # Create backup and version records
        await create_backup_and_version_records(
            ip=ip,
            retrieved_mac=retrieved_mac,
            deviceInfo=deviceInfo,
            cfg_full=cfg_full,
            info_full=info_full,
            state_full=state_full
        )
        
        # Return both MAC and the full deviceInfo
        return {
            "mac": mac,
            "device_info": deviceInfo
        }
    except Exception as e:
        logger.exception(f"Error processing device {ip}: {e}")
        # Mark device as offline if we have the MAC
        if existingMac:
            try:
                update_wled_device_partial({'status': 'offline'}, existingMac)
                logger.debug(f"Marked device {existingMac} as offline due to processing error")
            except Exception as update_error:
                logger.error(f"Failed to update status for device {existingMac}: {update_error}")
        return None

async def scan_and_import_devices(timeout: float = None):
    logger.info(f"Starting scan and import of devices")
    
    network_range = get_setting("network_range")
    if not network_range:
        local_ip = get_local_ip()
        network = ipaddress.IPv4Network(local_ip + '/24', strict=False)
        network_range = str(network)
    
    logger.info(f"Scanning network range: {network_range}")
    
    # First, scan for WLED devices
    loop = asyncio.get_running_loop()
    # Run synchronous scan_network in a separate thread to avoid blocking the event loop
    wled_ips = await loop.run_in_executor(None, scan_network, network_range, timeout)
    logger.info(f"Network scan found {len(wled_ips)} potential WLED devices: {wled_ips}")
    
    if not wled_ips:
        logger.info("No WLED devices found during network scan")
        return []
    
    imported = []
    ip_to_mac = {}  # Keep track of which MAC came from which IP
    
    # Create tasks for each IP
    tasks = [process_device(ip, None, timeout) for ip in wled_ips]
    # Run all tasks concurrently and gather results
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results and map successful imports to their source IPs
    for ip, result in zip(wled_ips, results):
        if isinstance(result, Exception):
            logger.error(f"Error processing device at {ip}: {result}")
            continue
        if result: 
            # Handle both old (string) and new (dict) return types for safety/compatibility
            if isinstance(result, dict) and 'mac' in result:
                mac_addr = result['mac']
            else:
                mac_addr = result
                
            ip_to_mac[ip] = mac_addr
            imported.append(mac_addr)
            logger.info(f"Successfully processed device at {ip} with MAC {mac_addr}")
    
    logger.info(f"Successfully processed {len(imported)} devices out of {len(wled_ips)} discovered IPs")
    for ip in wled_ips:
        if ip not in ip_to_mac:
            logger.warning(f"Device at {ip} was discovered but failed to process")

    return imported
