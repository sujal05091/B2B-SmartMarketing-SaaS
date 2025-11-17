from fastapi import APIRouter, Depends
from core.security import get_current_active_user
from models.user import User

router = APIRouter()

@router.get("/")
async def list_campaigns(current_user: User = Depends(get_current_active_user)):
    """List all campaigns for current user"""
    # TODO: Implement campaign listing
    return []

@router.post("/")
async def create_campaign(current_user: User = Depends(get_current_active_user)):
    """Create a new campaign"""
    # TODO: Implement campaign creation
    return {"message": "Campaign created"}
