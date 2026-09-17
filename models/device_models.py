from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List
from datetime import datetime
from .config_models import WLEDCfgDTO

class WLEDInfoDTO(BaseModel):
    arch: Optional[str] = None
    brand: Optional[str] = None
    build: Optional[int] = None
    core: Optional[str] = None
    freeheap: Optional[int] = None
    ip: Optional[str] = None
    mac: Optional[str] = None
    name: Optional[str] = None
    platform: Optional[str] = None
    product: Optional[str] = None
    udpport: Optional[int] = None
    uptime: Optional[int] = None
    version: Optional[str] = None
    wifi: Optional[Dict[str, Any]] = None

class WLEDStateDTO(BaseModel):
    on: Optional[bool] = None
    bri: Optional[int] = None
    transition: Optional[int] = None
    ps: Optional[int] = None
    pl: Optional[int] = None
    nl: Optional[Dict[str, Any]] = None
    udpn: Optional[Dict[str, Any]] = None
    seg: Optional[List[Dict[str, Any]]] = None

# Device DTOs
class WLEDDeviceBaseDTO(BaseModel):
    mac: str
    last_ip: Optional[str] = None
    local_name: Optional[str] = None
    hostname: Optional[str] = None
    name: Optional[str] = None
    adopted: Optional[bool] = False
    status: Optional[str] = None
    wifi_sleep: Optional[bool] = None  # Whether device has wifi sleep enabled
    turn_on_after_power_up: Optional[bool] = None  # Whether device turns on LEDs after power up
    mqtt_enabled: Optional[bool] = None  # Whether device has MQTT enabled
    usermod_url: Optional[str] = None

class WLEDDeviceCreateDTO(WLEDDeviceBaseDTO):
    pass

class WLEDDeviceUpdateDTO(BaseModel):
    last_ip: Optional[str] = None
    local_name: Optional[str] = None
    hostname: Optional[str] = None
    name: Optional[str] = None
    adopted: Optional[bool] = None
    status: Optional[str] = None
    mqtt_enabled: Optional[bool] = None
    usermod_url: Optional[str] = None

class WLEDDeviceDTO(WLEDDeviceBaseDTO):
    id: str
    last_seen: Optional[datetime] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None

# Full device info DTO
class WLEDDeviceFullInfoDTO(BaseModel):
    mac: str
    ip: str
    cfg_full: WLEDCfgDTO
    info_full: WLEDInfoDTO
    state_full: WLEDStateDTO
    has_static_ip: Optional[bool] = None  # Whether device has static IP configuration
    discovery_date_time: Optional[datetime] = None  # Created timestamp from wled_devices table
    device_id: Optional[str] = None  # Internal DB ID
    mqtt_enabled: Optional[bool] = None


# Device Short Info DTO
class DeviceShortInfoDTO(BaseModel):
    device_id: str
    mac: str
    name: Optional[str] = None
    last_seen: Optional[datetime] = None
    signal_strength: Optional[int] = None
    status: Optional[str] = None
    ip_address: Optional[str] = None
    software_version: Optional[str] = None
    state_on: Optional[bool] = None
    has_backups: bool = False
    has_static_ip: Optional[bool] = None  # Whether device has static IP configuration
    wifi_sleep: Optional[bool] = None  # Whether device has wifi sleep enabled
    turn_on_after_power_up: Optional[bool] = None  # Whether device turns on LEDs after power up
    mqtt_enabled: Optional[bool] = None  # Whether device has MQTT enabled
    usermod_url: Optional[str] = None
    architecture: Optional[str] = None
    brand: Optional[str] = None
    product: Optional[str] = None
    discovery_date_time: Optional[datetime] = None  # Created timestamp from wled_devices table
    # Keep old fields for compatibility
    id: Optional[str] = None
    last_ip: Optional[str] = None
    local_name: Optional[str] = None
    hostname: Optional[str] = None
    adopted: Optional[bool] = None
    version: Optional[str] = None
    signal: Optional[str] = None
    lastSeen: Optional[str] = None
    location: Optional[str] = None

# Device Full Details DTO
class DeviceFullDetailsDTO(BaseModel):
    # Basic device info
    device_id: str
    mac: str
    name: Optional[str] = None
    last_ip: Optional[str] = None
    local_name: Optional[str] = None
    hostname: Optional[str] = None
    adopted: bool = False
    status: Optional[str] = None
    last_seen: Optional[datetime] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    has_backups: bool = False
    discovery_date_time: Optional[datetime] = None  # Created timestamp from wled_devices table
    
    # Latest device data from versions table
    latest_info: Optional[Dict[str, Any]] = None  # Full info JSON
    latest_state: Optional[Dict[str, Any]] = None  # Full state JSON
    latest_config: Optional[Dict[str, Any]] = None  # Full config JSON
    latest_timestamp: Optional[datetime] = None
    
    # Extracted commonly used fields for convenience
    software_version: Optional[str] = None
    signal_strength: Optional[int] = None
    state_on: Optional[bool] = None
    brightness: Optional[int] = None
    current_preset: Optional[int] = None
    led_count: Optional[int] = None
    uptime: Optional[int] = None
    free_heap: Optional[int] = None
    wifi_rssi: Optional[int] = None
    wifi_channel: Optional[int] = None
    architecture: Optional[str] = None  # ESP8266 or ESP32
    has_static_ip: Optional[bool] = None  # Whether device has static IP configuration
    wifi_sleep: Optional[bool] = None  # Whether device has wifi sleep enabled
    turn_on_after_power_up: Optional[bool] = None  # Whether device turns on LEDs after power up
    mqtt_enabled: Optional[bool] = None  # Whether device has MQTT enabled
    usermod_url: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class AdoptDeviceRequest(BaseModel):
    device_id: str
    local_device_name: str
