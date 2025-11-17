"""
Configuration Management Module

Handles loading and accessing environment variables and application configuration.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class Config:
    """
    Configuration class to manage application settings and environment variables.
    
    Loads configuration from .env file and provides easy access to settings.
    """
    
    def __init__(self, env_file: str = ".env"):
        """
        Initialize configuration by loading environment variables.
        
        Args:
            env_file: Path to environment file
        """
        # Load environment variables
        env_path = Path(env_file)
        if env_path.exists():
            load_dotenv(env_path)
        else:
            print(f"Warning: {env_file} not found. Using default/system environment variables.")
        
        # OpenAI Configuration
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        self.OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        
        # Ollama Configuration (Alternative)
        self.OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")
        self.USE_OLLAMA = os.getenv("USE_OLLAMA", "false").lower() == "true"
        
        # Search API Configuration
        self.SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")
        self.BING_SEARCH_API_KEY = os.getenv("BING_SEARCH_API_KEY", "")
        self.GOOGLE_CUSTOM_SEARCH_API_KEY = os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY", "")
        self.GOOGLE_CUSTOM_SEARCH_ENGINE_ID = os.getenv("GOOGLE_CUSTOM_SEARCH_ENGINE_ID", "")
        
        # Contact Discovery APIs
        self.HUNTER_IO_API_KEY = os.getenv("HUNTER_IO_API_KEY", "")
        self.SNOV_IO_API_KEY = os.getenv("SNOV_IO_API_KEY", "")
        
        # Google Sheets Configuration
        self.GOOGLE_SHEETS_CREDENTIALS_FILE = os.getenv(
            "GOOGLE_SHEETS_CREDENTIALS_FILE",
            "config/google_credentials.json"
        )
        self.GOOGLE_SHEETS_SPREADSHEET_ID = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID", "")
        self.GOOGLE_SHEETS_WORKSHEET_NAME = os.getenv("GOOGLE_SHEETS_WORKSHEET_NAME", "Leads")
        
        # Google Drive Configuration
        self.GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")
        
        # Email Configuration
        self.SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
        self.SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
        self.SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
        self.SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
        self.SENDER_NAME = os.getenv("SENDER_NAME", "")
        
        # Application Settings
        self.MAX_LEADS_PER_RUN = int(os.getenv("MAX_LEADS_PER_RUN", "10"))
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "output"))
        self.PORTFOLIO_DIR = Path(os.getenv("PORTFOLIO_DIR", "output/portfolios"))
        
        # Rate Limiting
        self.API_RATE_LIMIT_DELAY = float(os.getenv("API_RATE_LIMIT_DELAY", "2"))
        self.MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
        
        # Create necessary directories
        self._create_directories()
    
    def _create_directories(self):
        """Create necessary directories if they don't exist."""
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.PORTFOLIO_DIR.mkdir(parents=True, exist_ok=True)
        Path("logs").mkdir(exist_ok=True)
    
    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate that required configuration is present.
        
        Returns:
            Tuple of (is_valid, list_of_missing_configs)
        """
        missing = []
        
        # Check AI configuration
        if not self.USE_OLLAMA and not self.OPENAI_API_KEY:
            missing.append("OPENAI_API_KEY (or enable USE_OLLAMA)")
        
        # Check search API
        if not any([self.SERPAPI_KEY, self.BING_SEARCH_API_KEY, 
                   self.GOOGLE_CUSTOM_SEARCH_API_KEY]):
            missing.append("At least one search API key (SERPAPI_KEY, BING_SEARCH_API_KEY, or GOOGLE_CUSTOM_SEARCH_API_KEY)")
        
        # Check Google Sheets
        if not self.GOOGLE_SHEETS_SPREADSHEET_ID:
            missing.append("GOOGLE_SHEETS_SPREADSHEET_ID")
        
        if not Path(self.GOOGLE_SHEETS_CREDENTIALS_FILE).exists():
            missing.append(f"Google credentials file at {self.GOOGLE_SHEETS_CREDENTIALS_FILE}")
        
        return (len(missing) == 0, missing)
    
    def get_config_summary(self) -> dict:
        """
        Get a summary of current configuration (without sensitive data).
        
        Returns:
            Dictionary with configuration summary
        """
        return {
            "ai_model": self.OLLAMA_MODEL if self.USE_OLLAMA else self.OPENAI_MODEL,
            "use_ollama": self.USE_OLLAMA,
            "search_api_configured": bool(self.SERPAPI_KEY or self.BING_SEARCH_API_KEY),
            "google_sheets_configured": bool(self.GOOGLE_SHEETS_SPREADSHEET_ID),
            "google_drive_configured": bool(self.GOOGLE_DRIVE_FOLDER_ID),
            "email_configured": bool(self.SMTP_USERNAME and self.SMTP_PASSWORD),
            "max_leads_per_run": self.MAX_LEADS_PER_RUN,
            "log_level": self.LOG_LEVEL
        }


# Global config instance
_config_instance: Optional[Config] = None


def get_config(env_file: str = ".env") -> Config:
    """
    Get or create global configuration instance.
    
    Args:
        env_file: Path to environment file
    
    Returns:
        Config instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config(env_file)
    return _config_instance
