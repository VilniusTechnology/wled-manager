"""
Device OTA firmware update API endpoints.
Extracted from devices.py for better maintainability.
"""
from fastapi import APIRouter, HTTPException, File, Form
from typing import List, Dict, Any
import asyncio
import logging
import time
import tempfile
import os
import json
import requests

from pydantic import BaseModel
from db.sqlite import get_latest_device_info
from models.dto import OTAUpdateResponse
from api.services.device_service import get_device_and_validate_ip, perform_ota_update

router = APIRouter()
logger = logging.getLogger(__name__)


class MassOTAUpdateResponse(BaseModel):
    success: bool
    message: str
    total_devices: int
    successful_updates: int
    failed_updates: int
    results: List[Dict[str, Any]]
    total_duration: float


@router.post("/devices/{device_id}/ota-update", response_model=OTAUpdateResponse, summary="Perform OTA firmware update on a WLED device")
async def perform_device_ota_update(device_id: str, firmware_file: bytes = File(...), filename: str = Form(...)):
    """Perform OTA firmware update on a WLED device by uploading firmware binary."""
    endpoint_start = time.time()

    logger.info(f"OTA update started for device: {device_id}, file: {filename}, size: {len(firmware_file)} bytes")

    device = get_device_and_validate_ip(device_id)
    
    # Get device architecture for firmware validation
    device_architecture = None
    try:
        latest_info = get_latest_device_info(device.mac)
        if latest_info and 'info' in latest_info and 'arch' in latest_info['info']:
            device_architecture = latest_info['info']['arch']
            logger.info(f"Device architecture: {device_architecture}")
    except Exception as e:
        logger.warning(f"Could not retrieve device architecture: {e}")
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
            temp_file.write(firmware_file)
            temp_file_path = temp_file.name

        try:
            # Perform OTA update
            result = await perform_ota_update(device.last_ip, temp_file_path, filename, device_architecture)

            total_duration = time.time() - endpoint_start
            result["total_duration"] = total_duration

            logger.info(f"OTA update completed for {device_id} in {total_duration:.2f}s")

            return OTAUpdateResponse(
                success=result["success"],
                message=result["message"],
                device_id=device_id,
                device_ip=device.last_ip,
                firmware_filename=filename,
                firmware_size=len(firmware_file),
                upload_duration=result.get("upload_duration"),
                device_response_status=result.get("device_response_status"),
                device_response_text=result.get("device_response_text"),
                steps_completed=result.get("steps_completed", []),
                warnings=result.get("warnings", [])
            )

        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except Exception as cleanup_error:
                logger.warning(f"Failed to clean up temporary file: {cleanup_error}")

    except HTTPException:
        raise
    except HTTPException:
        raise
    except requests.exceptions.RequestException as e:
        total_duration = time.time() - endpoint_start
        logger.error(f"Network error during OTA update for {device_id}: {e}")
        raise HTTPException(status_code=503, detail=f"Network error: {str(e)}")
    except Exception as e:
        total_duration = time.time() - endpoint_start
        logger.error(f"OTA update error for {device_id}: {e} (duration: {total_duration:.2f}s)")
        raise HTTPException(status_code=500, detail=f"OTA update failed: {str(e)}")


@router.post("/devices/ota-update-mass", response_model=MassOTAUpdateResponse, summary="Perform mass OTA firmware update on multiple WLED devices")
async def perform_mass_ota_update(firmware_file: bytes = File(...), device_ids: str = Form(...)):
    """Perform OTA firmware update on multiple WLED devices in parallel."""
    mass_start = time.time()

    logger.info(f"Mass OTA update started, firmware size: {len(firmware_file)} bytes")

    try:
        # Parse device IDs from form data
        device_ids_list = json.loads(device_ids)
        logger.info(f"Target devices: {len(device_ids_list)}")

        if not device_ids_list:
            raise HTTPException(status_code=400, detail="No device IDs provided")

        if len(device_ids_list) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 devices can be updated simultaneously")

        # Validate all devices exist and get their details
        devices = []
        for device_id in device_ids_list:
            device = get_device_and_validate_ip(device_id)
            devices.append(device)

        filename = f"mass_update_{int(time.time())}.bin"

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
            temp_file.write(firmware_file)
            temp_file_path = temp_file.name

        try:
            async def update_single_device(device):
                device_start = time.time()
                try:
                    # Get device architecture
                    device_architecture = None
                    try:
                        latest_info = get_latest_device_info(device.mac)
                        if latest_info and 'info' in latest_info and 'arch' in latest_info['info']:
                            device_architecture = latest_info['info']['arch']
                    except Exception:
                        pass

                    result = await perform_ota_update(device.last_ip, temp_file_path, filename, device_architecture)
                    device_duration = time.time() - device_start

                    return {
                        "device_id": device.id,
                        "device_name": device.name,
                        "mac": device.mac,
                        "ip": device.last_ip,
                        "success": True,
                        "duration": device_duration,
                        "result": result
                    }

                except Exception as e:
                    device_duration = time.time() - device_start
                    logger.error(f"OTA update failed for {device.name}: {e}")

                    return {
                        "device_id": device.id,
                        "device_name": device.name,
                        "mac": device.mac,
                        "ip": device.last_ip,
                        "success": False,
                        "duration": device_duration,
                        "error": str(e)
                    }

            # Execute all updates in parallel
            tasks = [update_single_device(device) for device in devices]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            successful_updates = 0
            failed_updates = 0
            processed_results = []

            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    failed_updates += 1
                    processed_results.append({
                        "device_id": devices[i].id if i < len(devices) else "unknown",
                        "device_name": devices[i].name if i < len(devices) else "unknown",
                        "success": False,
                        "error": str(result)
                    })
                else:
                    processed_results.append(result)
                    if result["success"]:
                        successful_updates += 1
                    else:
                        failed_updates += 1

            total_duration = time.time() - mass_start

            logger.info(f"Mass OTA completed: {successful_updates} successful, {failed_updates} failed in {total_duration:.2f}s")

            return MassOTAUpdateResponse(
                success=failed_updates == 0,
                message=f"Mass OTA update completed: {successful_updates} successful, {failed_updates} failed",
                total_devices=len(device_ids_list),
                successful_updates=successful_updates,
                failed_updates=failed_updates,
                results=processed_results,
                total_duration=total_duration
            )

        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except Exception as cleanup_error:
                logger.warning(f"Failed to clean up temporary file: {cleanup_error}")

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid device_ids JSON format")
    except HTTPException:
        raise
    except HTTPException:
        raise
    except requests.exceptions.RequestException as e:
        total_duration = time.time() - mass_start
        logger.error(f"Network error during Mass OTA update: {e}")
        raise HTTPException(status_code=503, detail=f"Network error: {str(e)}")
    except Exception as e:
        total_duration = time.time() - mass_start
        logger.error(f"Mass OTA update error: {e} (duration: {total_duration:.2f}s)")
        raise HTTPException(status_code=500, detail=f"Mass OTA update failed: {str(e)}")
