from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import EmailStr, Field

class User(Document):
    email: EmailStr = Field(..., unique=True, index=True)
    password_hash: str
    full_name: str
    company_name: Optional[str] = None
    avatar_url: Optional[str] = None
    plan: str = Field(default="free")  # free, pro, enterprise
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    lead_limit: int = Field(default=50)  # Monthly lead limit
    leads_used: int = Field(default=0)  # Leads used this month
    email_verified: bool = Field(default=False)
    is_admin: bool = Field(default=False)
    
    # API Keys for integrations
    serpapi_key: Optional[str] = None
    hunter_api_key: Optional[str] = None
    
    # AI Settings - Choose between OpenAI or Ollama
    ai_provider: str = Field(default="ollama")  # "openai" or "ollama"
    openai_api_key: Optional[str] = None
    ollama_base_url: Optional[str] = Field(default="http://localhost:11434")  # Default Ollama URL
    ollama_model: Optional[str] = Field(default="llama3.2:latest")  # Default model
    
    # Google Sheets Integration
    google_sheets_enabled: bool = Field(default=False)
    google_sheets_credentials: Optional[str] = None  # JSON string of credentials
    google_sheet_id: Optional[str] = None
    
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: Optional[str] = None
    smtp_from_name: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "users"
        indexes = [
            "email",
            "stripe_customer_id",
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "full_name": "John Doe",
                "company_name": "Acme Corp",
                "plan": "free",
            }
        }
