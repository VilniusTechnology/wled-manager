import logging
from db.sqlite import get_connection
import os

logger = logging.getLogger(__name__)

def get_backup_file_path(backup_id: str, file_type: str) -> str:
    """Get file path for a backup file and validate it exists."""
    column = "cfg_path" if file_type == "config" else "presets_path"
    filename = f"{file_type}_{backup_id}.json"

    with get_connection() as conn:
        cursor = conn.execute(f"SELECT {column} FROM wled_backups WHERE id = ?", (backup_id,))
        row = cursor.fetchone()

    if not row:
        logger.error(f"Backup {backup_id} not found")
        raise ValueError("Backup not found")

    file_path = row[0]

    if not os.path.exists(file_path):
        logger.error(f"{file_type.title()} file not found: {file_path}")
        raise ValueError(f"{file_type.title()} file not found")

    logger.info(f"Serving {file_type} file: {file_path}")
    return file_path