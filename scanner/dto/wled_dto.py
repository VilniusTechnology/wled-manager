# DTO for /json/cfg endpoint

# Import DTOs from dto directory
from .wled_cfg_dto import WLEDCfgDTO
from .wled_info_dto import WLEDInfoDTO
from .wled_state_dto import WLEDStateDTO
from utils.wled_config_utils import detect_static_ip_config

# DTO for WLED device full info

class WLEDDeviceFullInfoDTO:
    def __init__(self, mac, ip, cfg_full, info_full, state_full):
        self.mac = mac
        self.ip = ip
        self.cfg_full = WLEDCfgDTO(cfg_full)
        self.mqtt = self.cfg_full.mqtt
        self.network = self.cfg_full.nw
        self.info_full = WLEDInfoDTO(info_full)
        self.state_full = WLEDStateDTO(state_full)
        
        # Detect static IP configuration
        self.has_static_ip = None
        try:
            if cfg_full and isinstance(cfg_full, dict):
                self.has_static_ip = detect_static_ip_config(cfg_full)
        except Exception:
            # If detection fails, keep as None
            pass

    def to_dict(self):
        return {
            "mac": self.mac,
            "ip": self.ip,
            "mqtt": self.mqtt,
            "network": self.network,
            "cfg_full": self.cfg_full.to_dict(),
            "info_full": self.info_full.to_dict(),
            "state_full": self.state_full.to_dict(),
            "has_static_ip": self.has_static_ip
        }
