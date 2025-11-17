from fastapi import APIRouter, Depends
from core.security import get_current_active_user
from models.user import User

router = APIRouter()

@router.get("/me")
async def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user profile"""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "company_name": current_user.company_name,
        "avatar_url": current_user.avatar_url,
        "plan": current_user.plan,
        "email_verified": current_user.email_verified,
    }

@router.put("/me")
async def update_user_profile(
    full_name: str = None,
    company_name: str = None,
    current_user: User = Depends(get_current_active_user)
):
    """Update user profile"""
    if full_name:
        current_user.full_name = full_name
    if company_name:
        current_user.company_name = company_name
    
    await current_user.save()
    return {"message": "Profile updated successfully"}
