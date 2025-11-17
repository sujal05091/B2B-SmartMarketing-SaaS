from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from models.user import User
from models.lead import Lead
from core.security import get_current_active_user
from services.email_service import EmailService

router = APIRouter(prefix="/api/emails", tags=["emails"])

class SendEmailRequest(BaseModel):
    lead_id: str
    subject: Optional[str] = None
    body: Optional[str] = None

class TestSmtpRequest(BaseModel):
    pass

@router.post("/send")
async def send_email(
    request: SendEmailRequest,
    current_user: User = Depends(get_current_active_user),
):
    """Send an email to a specific lead"""
    # Get the lead
    lead = await Lead.get(request.lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    # Verify lead belongs to current user
    if lead.user != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this lead"
        )
    
    # Send the email
    result = await EmailService.send_email(
        user=current_user,
        lead=lead,
        subject=request.subject,
        body=request.body,
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Failed to send email")
        )
    
    return result

@router.post("/test-smtp")
async def test_smtp(
    current_user: User = Depends(get_current_active_user),
):
    """Test SMTP connection with current user's settings"""
    result = await EmailService.test_smtp_connection(current_user)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "SMTP connection failed")
        )
    
    return result

@router.get("/preview/{lead_id}")
async def preview_email(
    lead_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """Preview the email that would be sent to a lead"""
    # Get the lead
    lead = await Lead.get(lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )
    
    # Verify lead belongs to current user
    if lead.user != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this lead"
        )
    
    return {
        "to": lead.contact_email,
        "from": f"{current_user.smtp_from_name or current_user.full_name} <{current_user.smtp_from_email or current_user.email}>",
        "subject": lead.email_subject or f"Partnership Opportunity with {current_user.company_name}",
        "body": lead.email_body or "Hello, we'd like to discuss a partnership opportunity.",
        "company_name": lead.company_name,
        "website": lead.website,
    }
