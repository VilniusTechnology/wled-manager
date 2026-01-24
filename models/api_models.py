from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List
from datetime import datetime
from .device_models import WLEDDeviceFullInfoDTO

# Scan DTOs
class ScanResultDTO(BaseModel):
    devices: List[WLEDDeviceFullInfoDTO]

class WLEDDeviceVersionDTO(BaseModel):
    version_id: str
    mac: str
    timestamp: datetime
    ip: str
    device_id: Optional[str] = None
    has_config: bool = True

# Healthcheck DTOs (keeping existing ones but ensuring consistency)
class HealthcheckRequest(BaseModel):
    ips: List[str]

class DeviceStatus(BaseModel):
    ip: str
    status: str  # "online", "offline", "dead", "very_slow", "slow", "good", "excellent"
    last_seen: Optional[datetime] = None
    grade: Optional[int] = None  # 1=dead, 2=very_slow, 3=slow, 4=good, 5=excellent

class HealthcheckResponse(BaseModel):
    devices: List[DeviceStatus]

# WLED Config Update DTO
class WLEDConfigUpdateRequest(BaseModel):
    ip: str
    config: Dict[str, Any]
    timeout: float = 2.0

class WLEDConfigUpdateResponse(BaseModel):
    success: bool
    response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Generic response DTOs
class SuccessResponse(BaseModel):
    success: bool = True
    message: str

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None

class MassBackupResponse(BaseModel):
    success: bool = True
    message: str
    devices_backed_up: int
    total_devices: int
    failed_backups: int

# OTA Update Response DTO
class OTAUpdateResponse(BaseModel):
    success: bool
    message: str
    device_id: str
    device_ip: str
    firmware_filename: str
    firmware_size: int
    upload_duration: Optional[float] = None
    device_response_status: Optional[int] = None
    device_response_text: Optional[str] = None
    steps_completed: List[str] = []
    warnings: List[str] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Password DTOs
class PasswordRequest(BaseModel):
    key: Optional[str] = None
    password: str

class PasswordResponse(BaseModel):
    id: Optional[int] = None
    key: str
    password: str

# Settings DTOs
class AppSettingsDTO(BaseModel):
    settings: Dict[str, Any]

class SettingDTO(BaseModel):
    key: str
    value: Any
