from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, EmailStr, Field
from core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
)
from models.user import User
import secrets

router = APIRouter()

# Request/Response Models
class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    company_name: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

# Endpoints
@router.post("/signup", response_model=TokenResponse)
async def signup(request: SignupRequest, background_tasks: BackgroundTasks):
    """Register a new user"""
    # Check if user already exists
    existing_user = await User.find_one(User.email == request.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = User(
        email=request.email,
        password_hash=get_password_hash(request.password),
        full_name=request.full_name,
        company_name=request.company_name,
        email_verified=False,  # Should verify via email
    )
    await user.insert()
    
    # TODO: Send verification email
    # background_tasks.add_task(send_verification_email, user.email, verification_token)
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "company_name": user.company_name,
            "plan": user.plan,
            "email_verified": user.email_verified,
        }
    }

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login a user"""
    # Find user
    user = await User.find_one(User.email == request.email)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    # Verify password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "company_name": user.company_name,
            "plan": user.plan,
            "email_verified": user.email_verified,
            "avatar_url": user.avatar_url,
        }
    }

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout user (client should remove token)"""
    return {"message": "Successfully logged out"}

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, background_tasks: BackgroundTasks):
    """Request password reset"""
    user = await User.find_one(User.email == request.email)
    if not user:
        # Don't reveal if email exists
        return {"message": "If the email exists, a reset link has been sent"}
    
    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    # TODO: Store reset token with expiry in database
    # TODO: Send reset email
    # background_tasks.add_task(send_reset_email, user.email, reset_token)
    
    return {"message": "If the email exists, a reset link has been sent"}

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Reset password with token"""
    # TODO: Verify reset token
    # TODO: Update user password
    # For now, just return success
    return {"message": "Password reset successfully"}

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user"""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "company_name": current_user.company_name,
        "plan": current_user.plan,
        "lead_limit": current_user.lead_limit,
        "leads_used": current_user.leads_used,
        "email_verified": current_user.email_verified,
        "avatar_url": current_user.avatar_url,
        "created_at": current_user.created_at,
    }
