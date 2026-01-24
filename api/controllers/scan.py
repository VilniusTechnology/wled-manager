from fastapi import APIRouter, Query, HTTPException
import ipaddress
import logging
import datetime
from db.sqlite import get_wled_device, get_latest_device_info
from scanner.wled_scan import get_local_ip, scan_network
from api.services.scan_service import scan_and_import_devices, process_device
from models.dto import ScanResultDTO, WLEDDeviceDTO, WLEDDeviceFullInfoDTO, WLEDCfgDTO, WLEDInfoDTO, WLEDStateDTO

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/scan-network-import", response_model=ScanResultDTO, summary="Scan for WLED devices on the local network and return results as JSON")
async def scan_wled_devices(timeout: float = Query(None, description="Timeout in seconds for each device scan")):
    logger.info(f"Starting network scan view with timeout: {timeout}")
    
    imported_macs = await scan_and_import_devices(timeout)
    logger.info(f"Network scan completed. Found {len(imported_macs)} devices")

    results = []
    for mac in imported_macs:
        latest = get_latest_device_info(mac)
        db_device = get_wled_device(mac)
        if latest and db_device:
            # Merge DB device info with latest config/info/state
            wled_device_dto = WLEDDeviceFullInfoDTO(
                mac=mac,
                ip=latest.get("ip"),
                cfg_full=WLEDCfgDTO(**latest.get("cfg", {})),
                info_full=WLEDInfoDTO(**latest.get("info", {})),
                state_full=WLEDStateDTO(**latest.get("state", {})),
                has_static_ip=None,
                discovery_date_time=latest.get("timestamp"),
                device_id=getattr(db_device, "id", None)
            )
            # Attach extra DB fields to DTO (if present)
            # These fields are not in the Pydantic DTO, but can be added to the dict for frontend use
            dto_dict = wled_device_dto.dict()
            dto_dict.update({
                "name": getattr(db_device, "name", None),
                "hostname": getattr(db_device, "hostname", None),
                "local_name": getattr(db_device, "local_name", None),
                "last_ip": getattr(db_device, "last_ip", None),
                "adopted": getattr(db_device, "adopted", False),
                "status": getattr(db_device, "status", None),
                "last_seen": getattr(db_device, "last_seen", None),
                "created": getattr(db_device, "created", None),
                "updated": getattr(db_device, "updated", None),
            })
            results.append(dto_dict)
        elif latest:
            # Fallback: only config/info/state
            import hashlib
            from db.models import WLEDDevice
            from db.sqlite import insert_or_update_wled_device
            from api.services.scan_service import extract_device_details
            
            # Auto-heal: Create missing device record from latest version info
            logger.info(f"Auto-healing missing device record for {mac}")
            
            # Extract details using service helper
            temp_info = {
                "info_full": latest.get("info", {}),
                "state_full": latest.get("state", {}),
                "cfg_full": latest.get("cfg", {})
            }
            extra_details = extract_device_details(temp_info)
            
            # Determine hostname
            hostname = latest.get("cfg", {}).get("id", {}).get("mdns")
            if not hostname:
                hostname = latest.get("info", {}).get("name")

            device_data = WLEDDevice(
                mac=mac,
                last_ip=latest.get("ip"),
                local_name=latest.get("info", {}).get("name"),
                hostname=hostname,
                name=latest.get("info", {}).get("name"),
                adopted=False,
                last_seen=datetime.datetime.utcnow(),
                status='unknown',
                **extra_details
            )
            # This sets the ID to MD5 hash automatically in __init__
            device_id = device_data.id
            
            # Save to DB so subsequent lookups succeed
            try:
                insert_or_update_wled_device(device_data)
                logger.info(f"Successfully auto-healed device record for {mac} with ID {device_id}")
            except Exception as e:
                logger.error(f"Failed to auto-heal device record for {mac}: {e}")

            wled_device_dto = WLEDDeviceFullInfoDTO(
                mac=latest.get("mac"),
                ip=latest.get("ip"),
                cfg_full=WLEDCfgDTO(**latest.get("cfg", {})),
                info_full=WLEDInfoDTO(**latest.get("info", {})),
                state_full=WLEDStateDTO(**latest.get("state", {})),
                has_static_ip=None,
                discovery_date_time=latest.get("timestamp"),
                device_id=device_id
            )
            results.append(wled_device_dto.dict())


        else:
            logger.warning(f"Device processed but not found in database. MAC: {mac}")

    logger.info(f"Scan view completed. Retrieved info for {len(results)} devices")
    return ScanResultDTO(devices=results)

