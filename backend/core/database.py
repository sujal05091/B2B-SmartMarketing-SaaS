from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from core.config import settings
from models.user import User
from models.lead import Lead
from models.campaign import Campaign, CampaignRecipient
from models.subscription import Subscription
from models.usage import UsageTracking
from models.api_key import APIKey
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None

db = Database()

async def connect_db():
    """Connect to MongoDB and initialize Beanie"""
    try:
        db.client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
        
        # Test connection
        await db.client.admin.command('ping')
        logger.info("✅ Connected to MongoDB successfully!")
        
        await init_beanie(
            database=db.client[settings.MONGODB_DB_NAME],
            document_models=[
                User,
                Lead,
                Campaign,
                CampaignRecipient,
                Subscription,
                UsageTracking,
                APIKey,
            ],
        )
        logger.info("✅ Beanie initialized successfully!")
    except Exception as e:
        logger.warning(f"⚠️  MongoDB connection failed: {e}")
        logger.warning("⚠️  API will run but database operations will fail.")
        logger.warning("⚠️  Please start MongoDB: docker-compose up -d mongodb")

async def close_db():
    """Close MongoDB connection"""
    if db.client:
        db.client.close()
        logger.info("✅ MongoDB connection closed")
