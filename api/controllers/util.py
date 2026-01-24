from fastapi import FastAPI, Request, Response
import os
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
import logging
import time
from typing import Callable
import asyncio


from db import init_db

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="WLED Manager API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    logger.info(f"Request: {request.method} {request.url}")
    logger.debug(f"Headers: {dict(request.headers)}")
    
    # Log query parameters if any
    if request.query_params:
        logger.debug(f"Query params: {dict(request.query_params)}")
    
    # Log request body for POST/PUT/PATCH if it's not too large
    # Skip body logging for JSON endpoints to avoid conflicts with FastAPI parsing
    if request.method in ["POST", "PUT", "PATCH"]:
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            logger.debug(f"Request method: {request.method} with JSON content-type - skipping body logging to avoid parsing conflicts")
        elif "multipart/form-data" in content_type:
            logger.debug(f"Request method: {request.method} with multipart/form-data content-type - skipping body logging to avoid stream consumption")
        else:
            try:
                body = await request.body()
                if len(body) < 1000:  # Only log small bodies
                    logger.debug(f"Request body: {body.decode('utf-8', errors='ignore')}")
                else:
                    logger.debug(f"Request body: {len(body)} bytes (too large to log)")
            except Exception as e:
                logger.debug(f"Could not read request body: {e}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} - {process_time:.3f}s")
    
    return response

init_db()

def get_api_routes():
    """Get list of all API routes with their details."""
    routes = []
    for route in app.routes:
        if isinstance(route, APIRoute):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "summary": route.summary or "",
                "description": route.description or ""
            })
    return routes


@app.get("/")
def list_routes():
    """
    List all available endpoints in the API.
    """
    return {"endpoints": get_api_routes()}

@app.get("/health", summary="Health Check")
def health_check():
    """
    Health check endpoint for Kubernetes probes.
    Returns 200 OK if the service is running.
    """
    return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
    """Log all available endpoints to console on startup."""
    import os
    
    logger.info("WLED Manager API starting up...")
    logger.info("Initializing database connection...")
    init_db()
    logger.info("Database initialized successfully")
    
    # Start all schedulers via manager (which checks settings)
    try:
        from api.services.scheduler_manager import scheduler_manager
        results = await scheduler_manager.start_all_schedulers()
        logger.info(f"Schedulers initialization completed: {results}")
    except Exception as e:
        logger.error(f"Error starting schedulers: {e}")
    
    print("\n=== WLED Manager API Endpoints ===")
    routes = get_api_routes()
    for route in routes:
        methods = ','.join(route['methods'])
        summary = route['summary'] or "No summary"
        print(f"{methods:8} {route['path']:30} - {summary}")
    print("===================================\n")
    
    logger.info(f"API initialized with {len(routes)} endpoints")
    logger.debug("Available endpoints:")
    for route in routes:
        logger.debug(f"  {route['methods']} {route['path']} - {route['summary']}")

@app.on_event("shutdown")
async def shutdown_event():
    """Shut down background tasks gracefully."""
    logger.info("WLED Manager API shutting down...")
    
    # Stop backup scheduler if it was started
    try:
        from api.services.backup_scheduler import backup_scheduler
        if backup_scheduler.is_running:
            await backup_scheduler.stop()
            logger.info("Backup scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping backup scheduler: {e}")
        
    # Stop device refresh scheduler if it was started
    try:
        from api.services.device_refresh_scheduler import device_refresh_scheduler
        if device_refresh_scheduler.is_running:
            await device_refresh_scheduler.stop()
            logger.info("Device refresh scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping config version scheduler: {e}")



from api.controllers.scan import router as scan_router
from api.controllers.wled_config import router as wled_config_router
from api.controllers.backup import router as backup_router
from api.controllers.config_versions import router as config_versions_router
from api.controllers.settings import router as settings_router
from api.controllers.devices import router as devices_router
from api.controllers.device_backup import router as device_backup_router
from api.controllers.device_ota import router as device_ota_router
from api.controllers.scheduler import router as scheduler_router
from api.controllers.email_controller import router as email_router
from api.controllers.passwords import router as passwords_router

# Create an api router with /api prefix
from fastapi import APIRouter
api_router = APIRouter(prefix="/api")

# Include all routers under the /api prefix
api_router.include_router(scan_router)
api_router.include_router(wled_config_router)
api_router.include_router(backup_router)
api_router.include_router(config_versions_router)
api_router.include_router(settings_router)
api_router.include_router(devices_router)
api_router.include_router(device_backup_router)
api_router.include_router(device_ota_router)
api_router.include_router(scheduler_router)
api_router.include_router(email_router)
api_router.include_router(passwords_router)

# Include the api router in the main app
app.include_router(api_router)

