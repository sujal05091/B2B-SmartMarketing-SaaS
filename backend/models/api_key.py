from datetime import datetime
from typing import Optional
from beanie import Document, Link
from pydantic import Field
from models.user import User

class APIKey(Document):
    user: Link[User]
    key_hash: str
    name: str
    last_used_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    
    class Settings:
        name = "api_keys"
        indexes = [
            "user",
            "key_hash",
        ]
