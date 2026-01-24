from pydantic import BaseModel, Field, validator, field_validator
from typing import Optional, Any, Dict, List
import uuid

def convert_to_bool(value: Any) -> bool:
    """Convert various types to boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return bool(value)
    if isinstance(value, str):
        value = value.lower().strip()
        if value in ('true', '1', 'yes', 'on'):
            return True
        if value in ('false', '0', 'no', 'off'):
            return False
    raise ValueError(f'Invalid boolean value: {value}')

# WLED Configuration DTOs - Enhanced for full configuration support
class WLEDMQTTConfig(BaseModel):
    broker: Optional[str] = None
    port: Optional[int] = None
    user: Optional[str] = None
    psk: Optional[str] = None  # Password length (masked)
    cid: Optional[str] = None  # Client ID
    rtn: Optional[bool] = None  # Retain
    topics: Optional[Dict[str, str]] = None

class WLEDNetworkInterface(BaseModel):
    ssid: Optional[str] = None
    pskl: Optional[int] = None  # Password length (masked)
    ip: Optional[List[int]] = None
    gw: Optional[List[int]] = None
    sn: Optional[List[int]] = None

class WLEDNetworkConfig(BaseModel):
    ins: Optional[List[WLEDNetworkInterface]] = None
    gw: Optional[List[int]] = None
    sn: Optional[List[int]] = None
    dns: Optional[List[int]] = None

class WLEDAPConfig(BaseModel):
    ssid: Optional[str] = None
    pskl: Optional[int] = None  # Password length (masked)
    chan: Optional[int] = None
    hide: Optional[int] = None
    behav: Optional[int] = None
    ip: Optional[List[int]] = None

class WLEDWiFiConfig(BaseModel):
    sleep: Optional[bool] = None

class WLEDHardwareLEDConfig(BaseModel):
    total: Optional[int] = None
    maxpwr: Optional[int] = None
    ledma: Optional[int] = None
    cct: Optional[bool] = None
    cr: Optional[bool] = None
    cb: Optional[int] = None
    fps: Optional[int] = None
    rgbwm: Optional[int] = None
    ld: Optional[bool] = None
    ins: Optional[List[Dict[str, Any]]] = None

class WLEDHardwareButtonConfig(BaseModel):
    max: Optional[int] = None
    pull: Optional[bool] = None
    tt: Optional[int] = None
    mqtt: Optional[bool] = None
    ins: Optional[List[Dict[str, Any]]] = None

class WLEDHardwareIRConfig(BaseModel):
    pin: Optional[int] = None
    type: Optional[int] = None
    sel: Optional[bool] = None

class WLEDHardwareRelayConfig(BaseModel):
    pin: Optional[int] = None
    rev: Optional[bool] = None

class WLEDHardwareInterfaceConfig(BaseModel):
    i2c_pin: Optional[List[int]] = Field(default=None, alias="i2c-pin")
    spi_pin: Optional[List[int]] = Field(default=None, alias="spi-pin")

class WLEDHardwareConfig(BaseModel):
    led: Optional[WLEDHardwareLEDConfig] = None
    com: Optional[List[Dict[str, Any]]] = None
    btn: Optional[WLEDHardwareButtonConfig] = None
    ir: Optional[WLEDHardwareIRConfig] = None
    relay: Optional[WLEDHardwareRelayConfig] = None
    baud: Optional[int] = None
    if_: Optional[WLEDHardwareInterfaceConfig] = Field(default=None, alias="if")

class WLEDGammaCorrectionConfig(BaseModel):
    bri: Optional[float] = None
    col: Optional[float] = None
    val: Optional[float] = None

class WLEDTransitionConfig(BaseModel):
    mode: Optional[bool] = None
    dur: Optional[int] = None
    pal: Optional[int] = None
    rpc: Optional[int] = None

class WLEDNightlightConfig(BaseModel):
    mode: Optional[int] = None
    dur: Optional[int] = None
    tbri: Optional[int] = None
    macro: Optional[int] = None

class WLEDLightConfig(BaseModel):
    scale_bri: Optional[int] = Field(default=None, alias="scale-bri")
    pal_mode: Optional[int] = Field(default=None, alias="pal-mode")
    aseg: Optional[bool] = None
    gc: Optional[WLEDGammaCorrectionConfig] = None
    tr: Optional[WLEDTransitionConfig] = None
    nl: Optional[WLEDNightlightConfig] = None

class WLEDDefaultConfig(BaseModel):
    ps: Optional[int] = None
    on: Optional[bool] = None
    bri: Optional[int] = None

class WLEDSyncConfig(BaseModel):
    port0: Optional[int] = None
    port1: Optional[int] = None
    recv: Optional[Dict[str, Any]] = Field(default=None)  # Accept any type initially
    send: Optional[Dict[str, Any]] = None

    @validator('recv', pre=True)
    @classmethod
    def prevalidate_recv(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, bool]]:
        """Convert recv values to booleans before validation"""
        if v is None:
            return v
        try:
            return {k: convert_to_bool(val) for k, val in v.items()}
        except ValueError as e:
            # Keep the original value if conversion fails
            # This allows the standard validation to handle the error
            return v

    model_config = {
        'extra': 'allow',  # Allow extra fields
        'validate_assignment': True  # Validate when values are assigned
    }

class WLEDLiveConfig(BaseModel):
    en: Optional[bool] = None
    mso: Optional[bool] = None
    port: Optional[int] = None
    mc: Optional[bool] = None
    dmx: Optional[Dict[str, Any]] = None
    timeout: Optional[int] = None
    maxbri: Optional[bool] = None
    no_gc: Optional[bool] = Field(default=None, alias="no-gc")
    offset: Optional[int] = None

class WLEDMacroConfig(BaseModel):
    alexa: Optional[bool] = None
    macros: Optional[List[int]] = None
    p: Optional[int] = None

class WLEDMQTTInterfaceConfig(BaseModel):
    en: Optional[bool] = None
    broker: Optional[str] = None
    port: Optional[int] = None
    user: Optional[str] = None
    pskl: Optional[int] = None  # Password length (masked)
    cid: Optional[str] = None
    rtn: Optional[bool] = None
    topics: Optional[Dict[str, str]] = None

class WLEDHueConfig(BaseModel):
    en: Optional[bool] = None
    id: Optional[int] = None
    iv: Optional[int] = None
    recv: Optional[Dict[str, bool]] = None
    ip: Optional[List[int]] = None

class WLEDNTPConfig(BaseModel):
    en: Optional[bool] = None
    host: Optional[str] = None
    tz: Optional[int] = None
    offset: Optional[int] = None
    ampm: Optional[bool] = None
    ln: Optional[int] = None
    lt: Optional[int] = None

class WLEDInterfaceConfig(BaseModel):
    sync: Optional[WLEDSyncConfig] = None
    nodes: Optional[Dict[str, bool]] = None
    live: Optional[WLEDLiveConfig] = None
    va: Optional[WLEDMacroConfig] = None
    mqtt: Optional[WLEDMQTTInterfaceConfig] = None
    hue: Optional[WLEDHueConfig] = None
    ntp: Optional[WLEDNTPConfig] = None

class WLEDRemoteConfig(BaseModel):
    remote_enabled: Optional[bool] = None
    linked_remote: Optional[str] = None

class WLEDOliveConfig(BaseModel):
    clock: Optional[int] = None
    cntdwn: Optional[bool] = None
    min: Optional[int] = None
    max: Optional[int] = None
    o12pix: Optional[int] = None
    o5m: Optional[bool] = None
    osec: Optional[bool] = None

class WLEDTimersConfig(BaseModel):
    cntdwn: Optional[Dict[str, Any]] = None
    ins: Optional[List[Dict[str, Any]]] = None

class WLEDOTAConfig(BaseModel):
    lock: Optional[bool] = None
    lock_wifi: Optional[bool] = Field(default=None, alias="lock-wifi")
    pskl: Optional[int] = None  # Password length (masked)
    aota: Optional[bool] = None

class WLEDUMConfig(BaseModel):
    pass  # User mods configuration

class WLEDCfgDTO(BaseModel):
    rev: Optional[List[int]] = None
    vid: Optional[int] = None
    id: Optional[Dict[str, Any]] = None
    nw: Optional[WLEDNetworkConfig] = None
    ap: Optional[WLEDAPConfig] = None
    wifi: Optional[WLEDWiFiConfig] = None
    hw: Optional[WLEDHardwareConfig] = None
    light: Optional[WLEDLightConfig] = None
    def_: Optional[WLEDDefaultConfig] = Field(default=None, alias="def")
    if_: Optional[WLEDInterfaceConfig] = Field(default=None, alias="if")
    remote: Optional[WLEDRemoteConfig] = None
    ol: Optional[WLEDOliveConfig] = None
    timers: Optional[WLEDTimersConfig] = None
    ota: Optional[WLEDOTAConfig] = None
    um: Optional[WLEDUMConfig] = None
    mqtt: Optional[WLEDMQTTConfig] = None

    class Config:
        allow_population_by_field_name = True
