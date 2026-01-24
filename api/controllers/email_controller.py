from fastapi import APIRouter, HTTPException
from models.dto import SuccessResponse
from api.services.email_service import EmailService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/email/backup", response_model=SuccessResponse, summary="Send backup email")
def send_backup_email():
    """Trigger sending the backup email with device links."""
    logger.info("Triggering backup email")
    email_service = EmailService()
    success, error_msg = email_service.send_backup_email()
    
    if success:
        return SuccessResponse(message="Backup email sent successfully")
    else:
        raise HTTPException(status_code=500, detail=f"Failed to send backup email: {error_msg}")

@router.post("/email/test", response_model=SuccessResponse, summary="Send test email")
def send_test_email():
    """Send a test email to verify SMTP configuration."""
    logger.info("Sending test email")
    email_service = EmailService()
    success, error_msg = email_service.send_email("WLED Manager Test Email", "<p>This is a test email from WLED Manager.</p>")
    
    if success:
        return SuccessResponse(message="Test email sent successfully")
    else:
        raise HTTPException(status_code=500, detail=f"Failed to send test email: {error_msg}")
