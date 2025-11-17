from datetime import datetime
from typing import Optional
from beanie import Document, Link
from pydantic import Field
from models.user import User
from models.lead import Lead

class Campaign(Document):
    user: Link[User]
    name: str
    subject: Optional[str] = None
    body: Optional[str] = None
    status: str = Field(default="draft")  # draft, scheduled, sent, sending
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    recipients_count: int = Field(default=0)
    opens_count: int = Field(default=0)
    clicks_count: int = Field(default=0)
    replies_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "campaigns"
        indexes = [
            "user",
            "status",
            "created_at",
        ]

class CampaignRecipient(Document):
    campaign: Link[Campaign]
    lead: Link[Lead]
    status: str = Field(default="pending")  # pending, sent, opened, clicked, replied, bounced
    sent_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Settings:
        name = "campaign_recipients"
        indexes = [
            "campaign",
            "lead",
            "status",
        ]
