from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
from api.services.scheduler_manager import scheduler_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/schedulers", tags=["schedulers"])

@router.get("")
async def get_all_schedulers() -> Dict[str, Any]:
    """Get status of all schedulers."""
    try:
        statuses = scheduler_manager.get_all_scheduler_statuses()
        return {
            'success': True,
            'schedulers': statuses
        }
    except Exception as e:
        logger.error(f"Error getting scheduler statuses: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{scheduler_name}")
async def get_scheduler_status(scheduler_name: str) -> Dict[str, Any]:
    """Get status of a specific scheduler."""
    try:
        status = scheduler_manager.get_scheduler_status(scheduler_name)
        return {
            'success': True,
            'scheduler': status
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting scheduler {scheduler_name} status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{scheduler_name}/start")
async def start_scheduler(scheduler_name: str) -> Dict[str, Any]:
    """Start a specific scheduler."""
    try:
        result = await scheduler_manager.start_scheduler(scheduler_name)
        return {
            'success': result,
            'message': f"Scheduler {scheduler_name} {'started' if result else 'failed to start'}"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error starting scheduler {scheduler_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{scheduler_name}/stop")
async def stop_scheduler(scheduler_name: str) -> Dict[str, Any]:
    """Stop a specific scheduler."""
    try:
        result = await scheduler_manager.stop_scheduler(scheduler_name)
        return {
            'success': result,
            'message': f"Scheduler {scheduler_name} {'stopped' if result else 'failed to stop'}"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error stopping scheduler {scheduler_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{scheduler_name}/run")
async def run_scheduler_now(scheduler_name: str) -> Dict[str, Any]:
    """Trigger immediate execution of a scheduler."""
    try:
        result = await scheduler_manager.run_scheduler_now(scheduler_name)
        return {
            'success': result,
            'message': f"Scheduler {scheduler_name} {'executed successfully' if result else 'execution failed'}"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error running scheduler {scheduler_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop-all")
async def stop_all_schedulers() -> Dict[str, Any]:
    """Stop all schedulers."""
    try:
        results = await scheduler_manager.stop_all_schedulers()
        return {
            'success': all(results.values()),
            'results': results,
            'message': "All schedulers stop operation completed"
        }
    except Exception as e:
        logger.error(f"Error stopping all schedulers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/network_scan/results")
async def get_last_scan_results() -> Dict[str, Any]:
    """Get the results from the last network scan."""
    try:
        from api.services.scan_scheduler import scan_scheduler
        results = scan_scheduler.get_last_scan_results()
        
        if results:
            return {
                'success': True,
                'results': results
            }
        else:
            return {
                'success': True,
                'results': None,
                'message': 'No scan results available yet'
            }
    except Exception as e:
        logger.error(f"Error getting scan results: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop-all")
async def stop_all_schedulers() -> Dict[str, Any]:
    """Stop all schedulers."""
    try:
        results = await scheduler_manager.stop_all_schedulers()
        return {
            'success': all(results.values()),
            'results': results,
            'message': "All schedulers stop operation completed"
        }
    except Exception as e:
        logger.error(f"Error stopping all schedulers: {e}")
        raise HTTPException(status_code=500, detail=str(e))