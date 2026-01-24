
import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional
import uuid
import sys
from dotenv import load_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.sqlite import insert_backup
from services.settings_service import get_setting

class WLEDBackupRetriever:
    """
    Retrieves and saves WLED device backups (presets.json and cfg.json).
    Backups are saved under a directory named after the device's MAC address.
    Each backup is versioned by datetime.
    Backup directory can be set via BACKUP_DIR env variable or .env file.
    """
    def __init__(self, backup_dir: Optional[str] = None):
        load_dotenv()
        self.backup_dir = backup_dir or get_setting("backup_dir")
        os.makedirs(self.backup_dir, exist_ok=True)

    def get_mac_address(self, ip_address: str) -> Optional[str]:
        """
        Retrieves the MAC address from the WLED device info endpoint.
        """
        try:
            timeout = get_setting("backup_info_timeout")
            resp = requests.get(f"http://{ip_address}/json/info", timeout=timeout)
            resp.raise_for_status()
            info = resp.json()
            return info.get("mac")
        except Exception as e:
            print(f"Failed to get MAC address from {ip_address}: {e}")
            return None

    def download_file(self, ip_address: str, filename: str) -> Optional[bytes]:
        url = f"http://{ip_address}/edit?download=/{filename}"
        try:
            timeout = get_setting("backup_download_timeout")
            resp = requests.get(url, timeout=timeout)
            resp.raise_for_status()
            return resp.content
        except Exception as e:
            print(f"Failed to download {filename} from {ip_address}: {e}")
            return None

    def backup_device(self, ip_address: str) -> Optional[str]:
        mac = self.get_mac_address(ip_address)
        if not mac:
            print(f"Could not retrieve MAC address for {ip_address}")
            return None
        device_dir = os.path.join(self.backup_dir, mac)
        os.makedirs(device_dir, exist_ok=True)
        
        # Get configured timezone, defaulting to UTC if not set
        timezone_name = get_setting("timezone") or "UTC"
        try:
            tz = ZoneInfo(timezone_name)
        except Exception:
            tz = ZoneInfo("UTC")
        timestamp = datetime.now(tz).strftime("%Y%m%d_%H%M%S")
        files = ["presets.json", "cfg.json"]
        backup_paths = {}
        for fname in files:
            content = self.download_file(ip_address, fname)
            if content:
                backup_path = os.path.join(device_dir, f"{fname}.{timestamp}")
                with open(backup_path, "wb") as f:
                    f.write(content)
                print(f"Saved {fname} for {mac} at {backup_path}")
                backup_paths[fname] = backup_path
            else:
                print(f"Failed to backup {fname} for {mac}")
        # Persist backup reference to db if both files were saved
        if "presets.json" in backup_paths and "cfg.json" in backup_paths:
            from db.backup_models import WLEDBackupDBModel
            backup_ref = WLEDBackupDBModel(
                mac=mac,
                timestamp=timestamp,
                presets_path=backup_paths["presets.json"],
                cfg_path=backup_paths["cfg.json"]
            )
            insert_backup(backup_ref)
        return device_dir
