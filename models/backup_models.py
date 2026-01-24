from pydantic import BaseModel
from typing import Optional

# Backup DTOs
class WLEDBackupDTO(BaseModel):
    id: str
    mac: str
    timestamp: str
    presets_path: str
    cfg_path: str

class WLEDBackupCreateDTO(BaseModel):
    mac: str
    timestamp: str
    presets_path: str
    cfg_path: str
