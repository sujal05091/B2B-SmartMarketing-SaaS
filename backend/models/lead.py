from datetime import datetime
from typing import Optional, List
from beanie import Document, Link
from pydantic import Field, HttpUrl
from models.user import User

class Lead(Document):
    user: Link[User]
    company_name: str
    website: Optional[str] = None
    industry: Optional[str] = None
    services: Optional[str] = None
    matched_services: List[str] = Field(default_factory=list)
    contact_email: Optional[str] = None
    email_subject: Optional[str] = None
    email_body: Optional[str] = None
    portfolio_path: Optional[str] = None
    status: str = Field(default="new")  # new, contacted, replied, bounced
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "leads"
        indexes = [
            "user",
            "status",
            "contact_email",
            "created_at",
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "company_name": "Acme Corp",
                "website": "https://acmecorp.com",
                "industry": "Technology",
                "contact_email": "contact@acmecorp.com",
                "status": "new",
            }
        }
