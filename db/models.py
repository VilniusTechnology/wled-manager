from pydantic import BaseModel, Field
from typing import Optional, Any
import uuid
import hashlib
from datetime import datetime

class AppConfig(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    settings: Any  # JSON field for all settings

    class Config:
        from_attributes = True

class WLEDDeviceDBModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    mac: str
    mac_original: str
    ip: str
    mqtt: Optional[str] = None  # JSON string
    network: Optional[str] = None  # JSON string
    cfg_full: str  # JSON string
    info_full: str  # JSON string
    state_full: str  # JSON string
    device_id: Optional[str] = None  # Generated from MAC if not provided

    class Config:
        from_attributes = True

    def __init__(self, **data):
        super().__init__(**data)
        if not self.device_id and self.mac:
            self.device_id = hashlib.md5(self.mac.encode()).hexdigest()

class WLEDDevice(BaseModel):
    id: Optional[str] = None  # Generated from MAC if not provided
    mac: str
    last_ip: Optional[str] = None
    local_name: Optional[str] = None
    hostname: Optional[str] = None
    name: Optional[str] = None
    adopted: Optional[bool] = False
    last_seen: Optional[datetime] = None
    status: Optional[str] = None  # Health status: dead, very_slow, slow, good, excellent
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    software_version: Optional[str] = None
    wifi_signal: Optional[int] = None
    state_on: Optional[bool] = None
    architecture: Optional[str] = None
    led_count: Optional[int] = None
    has_static_ip: Optional[bool] = None
    wifi_sleep: Optional[bool] = None
    turn_on_after_power_up: Optional[bool] = None
    mqtt_enabled: Optional[bool] = None
    usermod_url: Optional[str] = None

    class Config:
        from_attributes = True

    def __init__(self, **data):
        super().__init__(**data)
        if not self.id and self.mac:
            import hashlib
            self.id = hashlib.md5(self.mac.encode()).hexdigest()

class WLEDDeviceVersion(BaseModel):
    version_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    mac: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ip: str
    mqtt: Optional[str] = None  # JSON string
    network: Optional[str] = None  # JSON string
    cfg_full: str  # JSON string
    info_full: str  # JSON string
    state_full: str  # JSON string
    device_id: Optional[str] = None  # Optional device_id field - MD5 hash of MAC, references wled_devices.id

    class Config:
        from_attributes = True

    def __init__(self, **data):
        super().__init__(**data)
        if not self.device_id and self.mac:
            self.device_id = hashlib.md5(self.mac.encode()).hexdigest()