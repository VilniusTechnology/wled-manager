from api.controllers.util import app
import os
import logging

# Map LOG_LEVEL string to logging constants
LOG_LEVEL_MAP = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}

def get_log_level():
    """Get log level from environment variable."""
    level_str = os.getenv("LOG_LEVEL", "info").lower()
    return LOG_LEVEL_MAP.get(level_str, logging.INFO)

# Configure logging with environment-based level
logging.basicConfig(
    level=get_log_level(),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    version = os.getenv("VERSION", "unknown")
    logger.info(f"Starting WLED Manager API version: {version}")
