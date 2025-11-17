from datetime import datetime
from typing import Optional
from beanie import Document, Link
from pydantic import Field
from models.user import User

class Subscription(Document):
    user: Link[User]
    plan: str  # pro, enterprise
    status: str = Field(default="active")  # active, canceled, past_due, trialing
    stripe_subscription_id: Optional[str] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "subscriptions"
        indexes = [
            "user",
            "stripe_subscription_id",
            "status",
        ]
