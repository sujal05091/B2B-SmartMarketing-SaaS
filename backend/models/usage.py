from datetime import datetime
from beanie import Document, Link
from pydantic import Field
from models.user import User

class UsageTracking(Document):
    user: Link[User]
    month: datetime  # First day of the month
    leads_discovered: int = Field(default=0)
    emails_sent: int = Field(default=0)
    api_calls: int = Field(default=0)
    pdfs_generated: int = Field(default=0)
    
    class Settings:
        name = "usage_tracking"
        indexes = [
            "user",
            "month",
            [("user", 1), ("month", 1)],  # Compound unique index
        ]
