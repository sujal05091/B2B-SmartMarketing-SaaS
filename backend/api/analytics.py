from fastapi import APIRouter, Depends
from core.security import get_current_active_user
from models.user import User
from models.lead import Lead
from models.usage import UsageTracking
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_stats(current_user: User = Depends(get_current_active_user)):
    """Get dashboard analytics"""
    # Count total leads
    total_leads = await Lead.find(Lead.user.ref.id == current_user.id).count()

    # Count contacted leads
    contacted = await Lead.find(
        Lead.user.ref.id == current_user.id,
        Lead.status == "contacted"
    ).count()

    # Get current month usage
    current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    usage = await UsageTracking.find_one(
        UsageTracking.user.id == current_user.id,
        UsageTracking.month == current_month
    )

    emails_sent = usage.emails_sent if usage else 0

    return {
        "total_leads": total_leads,
        "emails_sent": emails_sent,
        "success_rate": round((contacted / total_leads * 100), 1) if total_leads > 0 else 0,
    }
