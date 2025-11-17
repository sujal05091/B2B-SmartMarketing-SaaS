from fastapi import APIRouter, Depends
from core.security import get_admin_user
from models.user import User

router = APIRouter()

@router.get("/users")
async def list_all_users(admin: User = Depends(get_admin_user)):
    """List all users (admin only)"""
    users = await User.find_all().to_list()
    return [
        {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "plan": user.plan,
            "created_at": user.created_at,
        }
        for user in users
    ]
