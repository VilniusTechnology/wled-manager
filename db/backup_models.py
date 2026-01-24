from pydantic import BaseModel, Field
from typing import Optional
import uuid
import hashlib

class WLEDBackupDBModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    mac: str
    timestamp: str
    presets_path: str
    cfg_path: str
    device_id: Optional[str] = None  # Generated from MAC if not provided

    class Config:
        from_attributes = True

    def __init__(self, **data):
        super().__init__(**data)
        if not self.device_id and self.mac:
            self.device_id = hashlib.md5(self.mac.encode()).hexdigest()
