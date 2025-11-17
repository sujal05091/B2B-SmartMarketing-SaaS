from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from core.database import connect_db, close_db
from core.config import settings
from api import auth, users, leads, campaigns, billing, analytics, admin, settings as settings_api, emails, chatbot

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        print("🚀 Starting up the application...")
        await connect_db()
        print("✅ Database connected successfully!")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        # Don't raise exception, let app start anyway
        # raise
    yield
    # Shutdown
    try:
        await close_db()
        print("✅ Database connection closed!")
    except Exception as e:
        print(f"❌ Error closing database: {e}")

app = FastAPI(
    title="LeadGen AI API",
    description="B2B Smart Marketing Assistant API",
    version="1.0.0",
    lifespan=lifespan,  # Enable lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(leads.router, prefix="/api/leads", tags=["Leads"])
app.include_router(emails.router, tags=["Emails"])
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["Campaigns"])
app.include_router(billing.router, prefix="/api/billing", tags=["Billing"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(settings_api.router, prefix="/api/settings", tags=["Settings"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(chatbot.router, prefix="/api/chatbot", tags=["Chatbot"])

@app.get("/")
async def root():
    return {
        "message": "LeadGen AI API",
        "version": "1.0.0",
        "docs": "/docs",
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
