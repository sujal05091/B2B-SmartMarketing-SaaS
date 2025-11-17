from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from core.security import get_current_active_user
from models.user import User
from datetime import datetime

router = APIRouter()

class ApiKeysUpdate(BaseModel):
    serpapi_key: Optional[str] = None
    hunter_api_key: Optional[str] = None
    ai_provider: Optional[str] = None  # "openai" or "ollama"
    openai_api_key: Optional[str] = None
    ollama_base_url: Optional[str] = None
    ollama_model: Optional[str] = None

class SmtpSettingsUpdate(BaseModel):
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: Optional[EmailStr] = None
    smtp_from_name: Optional[str] = None

class GoogleSheetsUpdate(BaseModel):
    google_sheets_enabled: Optional[bool] = None
    google_sheets_credentials: Optional[str] = None  # JSON string
    google_sheet_id: Optional[str] = None

class SettingsResponse(BaseModel):
    # API Keys (masked for security)
    serpapi_key_set: bool
    hunter_api_key_set: bool
    
    # AI Settings
    ai_provider: str
    openai_api_key_set: bool
    ollama_base_url: Optional[str] = None
    ollama_model: Optional[str] = None
    
    # Google Sheets
    google_sheets_enabled: bool
    google_sheets_configured: bool
    google_sheet_id: Optional[str] = None
    
    # SMTP Settings (masked passwords)
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password_set: bool
    smtp_from_email: Optional[str] = None
    smtp_from_name: Optional[str] = None

@router.get("/", response_model=SettingsResponse)
async def get_settings(current_user: User = Depends(get_current_active_user)):
    """Get current user's settings (API keys masked)"""
    from core.config import settings
    
    return SettingsResponse(
        serpapi_key_set=bool(current_user.serpapi_key),
        hunter_api_key_set=bool(current_user.hunter_api_key),
        ai_provider=current_user.ai_provider or "ollama",
        openai_api_key_set=bool(current_user.openai_api_key),
        ollama_base_url=current_user.ollama_base_url or settings.OLLAMA_BASE_URL,
        ollama_model=current_user.ollama_model or settings.OLLAMA_MODEL,
        google_sheets_enabled=current_user.google_sheets_enabled,
        google_sheets_configured=bool(current_user.google_sheets_credentials),
        google_sheet_id=current_user.google_sheet_id,
        smtp_host=current_user.smtp_host or settings.SMTP_HOST,
        smtp_port=current_user.smtp_port or settings.SMTP_PORT,
        smtp_username=current_user.smtp_username or settings.SMTP_USERNAME,
        smtp_password_set=bool(current_user.smtp_password),
        smtp_from_email=current_user.smtp_from_email or settings.SENDER_EMAIL,
        smtp_from_name=current_user.smtp_from_name or settings.SENDER_NAME,
    )

@router.put("/api-keys")
async def update_api_keys(
    keys: ApiKeysUpdate,
    current_user: User = Depends(get_current_active_user),
):
    """Update API keys for integrations"""
    if keys.serpapi_key is not None:
        current_user.serpapi_key = keys.serpapi_key
    if keys.hunter_api_key is not None:
        current_user.hunter_api_key = keys.hunter_api_key
    if keys.ai_provider is not None:
        current_user.ai_provider = keys.ai_provider
    if keys.openai_api_key is not None:
        current_user.openai_api_key = keys.openai_api_key
    if keys.ollama_base_url is not None:
        current_user.ollama_base_url = keys.ollama_base_url
    if keys.ollama_model is not None:
        current_user.ollama_model = keys.ollama_model
    
    current_user.updated_at = datetime.utcnow()
    await current_user.save()
    
    return {"message": "API keys updated successfully"}

@router.put("/smtp")
async def update_smtp_settings(
    smtp: SmtpSettingsUpdate,
    current_user: User = Depends(get_current_active_user),
):
    """Update SMTP settings for email sending"""
    if smtp.smtp_host is not None:
        current_user.smtp_host = smtp.smtp_host
    if smtp.smtp_port is not None:
        current_user.smtp_port = smtp.smtp_port
    if smtp.smtp_username is not None:
        current_user.smtp_username = smtp.smtp_username
    if smtp.smtp_password is not None:
        current_user.smtp_password = smtp.smtp_password
    if smtp.smtp_from_email is not None:
        current_user.smtp_from_email = smtp.smtp_from_email
    if smtp.smtp_from_name is not None:
        current_user.smtp_from_name = smtp.smtp_from_name
    
    current_user.updated_at = datetime.utcnow()
    await current_user.save()
    
    return {"message": "SMTP settings updated successfully"}

@router.put("/google-sheets")
async def update_google_sheets(
    sheets: GoogleSheetsUpdate,
    current_user: User = Depends(get_current_active_user),
):
    """Update Google Sheets integration settings"""
    if sheets.google_sheets_enabled is not None:
        current_user.google_sheets_enabled = sheets.google_sheets_enabled
    if sheets.google_sheets_credentials is not None:
        current_user.google_sheets_credentials = sheets.google_sheets_credentials
    if sheets.google_sheet_id is not None:
        current_user.google_sheet_id = sheets.google_sheet_id
    
    current_user.updated_at = datetime.utcnow()
    await current_user.save()
    
    return {"message": "Google Sheets settings updated successfully"}

@router.delete("/api-keys/{key_name}")
async def delete_api_key(
    key_name: str,
    current_user: User = Depends(get_current_active_user),
):
    """Delete a specific API key"""
    valid_keys = ["serpapi_key", "hunter_api_key", "openai_api_key"]
    if key_name not in valid_keys:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid key name. Must be one of: {', '.join(valid_keys)}"
        )
    
    setattr(current_user, key_name, None)
    current_user.updated_at = datetime.utcnow()
    await current_user.save()
    
    return {"message": f"{key_name} deleted successfully"}
