from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from pydantic import BaseModel, Field, HttpUrl
from core.security import get_current_active_user
from models.user import User
from models.lead import Lead
from datetime import datetime
from beanie import PydanticObjectId

router = APIRouter()

# Request/Response Models
class DiscoverLeadsRequest(BaseModel):
    business_name: str
    business_desc: str
    website: Optional[str] = None
    target_industry: Optional[str] = None
    target_region: Optional[str] = None
    max_leads: int = Field(default=10, ge=1, le=100)
    find_emails: bool = Field(default=True)
    generate_pdfs: bool = Field(default=True)

class LeadResponse(BaseModel):
    id: str
    company_name: str
    website: Optional[str]
    industry: Optional[str]
    services: Optional[str]
    contact_email: Optional[str]
    email_subject: Optional[str]
    email_body: Optional[str]
    portfolio_path: Optional[str]
    status: str
    created_at: datetime

class DiscoverLeadsResponse(BaseModel):
    task_id: str
    status: str
    message: str

class UpdateLeadRequest(BaseModel):
    company_name: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    contact_email: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

# Endpoints
@router.post("/discover", response_model=DiscoverLeadsResponse)
async def discover_leads(
    request: DiscoverLeadsRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
):
    """
    Start lead discovery process (runs in background)
    Integrates with existing SmartMarketingAssistant
    """
    print(f"🎯 DISCOVER LEADS ENDPOINT HIT!")
    print(f"   User: {current_user.email}")
    print(f"   Request: {request.dict()}")
    
    from services.lead_discovery_service import discover_leads_task
    
    # Check lead limits
    if current_user.leads_used + request.max_leads > current_user.lead_limit:
        remaining_leads = current_user.lead_limit - current_user.leads_used
        if remaining_leads <= 0:
            raise HTTPException(
                status_code=402,
                detail="Lead limit exceeded. Upgrade your plan to generate more leads."
            )
        else:
            raise HTTPException(
                status_code=402,
                detail=f"You can only generate {remaining_leads} more leads this month. Upgrade your plan for more."
            )
    
    # Check usage limits based on plan
    # Free: 10, Pro: 100, Enterprise: unlimited
    limits = {"free": 10, "pro": 100, "enterprise": 999999}
    max_allowed = limits.get(current_user.plan, 10)
    
    if request.max_leads > max_allowed:
        raise HTTPException(
            status_code=403,
            detail=f"Your {current_user.plan} plan allows up to {max_allowed} leads"
        )
    
    # TODO: Check monthly usage limit
    
    # Start background task
    task_id = f"discover_{current_user.id}_{datetime.utcnow().timestamp()}"
    print(f"   Task ID: {task_id}")
    print(f"   Adding background task...")
    
    background_tasks.add_task(
        discover_leads_task,
        task_id=task_id,
        user_id=str(current_user.id),
        request_data=request.dict(),
    )
    
    print(f"   ✅ Background task added!")
    
    return {
        "task_id": task_id,
        "status": "started",
        "message": "Lead discovery started. This may take a few minutes.",
    }

@router.get("/", response_model=List[LeadResponse])
async def get_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    industry: Optional[str] = None,
    has_email: Optional[bool] = None,
    current_user: User = Depends(get_current_active_user),
):
    """Get all leads for current user with pagination and filters"""
    print(f"📊 GET LEADS ENDPOINT HIT!")
    print(f"   User: {current_user.email}")
    print(f"   User ID: {current_user.id}")
    print(f"   Filters: skip={skip}, limit={limit}, status={status}, industry={industry}")
    
    # First check total leads in database
    total_leads = await Lead.count()
    print(f"   Total leads in database: {total_leads}")
    
    # Fix: Use Lead.user directly for Link field comparison (contains ObjectId)
    query = Lead.find(Lead.user == current_user.id)
    
    if status:
        query = query.find(Lead.status == status)
    if industry:
        query = query.find(Lead.industry == industry)
    if has_email is not None:
        if has_email:
            query = query.find(Lead.contact_email != None)
        else:
            query = query.find(Lead.contact_email == None)
    
    leads = await query.sort(-Lead.created_at).skip(skip).limit(limit).to_list()
    
    print(f"   Found {len(leads)} leads for this user")
    if len(leads) > 0:
        print(f"   First lead: {leads[0].company_name}")
    
    return [
        LeadResponse(
            id=str(lead.id),
            company_name=lead.company_name,
            website=lead.website,
            industry=lead.industry,
            services=lead.services,
            contact_email=lead.contact_email,
            email_subject=lead.email_subject,
            email_body=lead.email_body,
            portfolio_path=lead.portfolio_path,
            status=lead.status,
            created_at=lead.created_at,
        )
        for lead in leads
    ]

@router.get("/stats")
async def get_lead_stats(
    current_user: User = Depends(get_current_active_user),
):
    """Get lead statistics for debugging"""
    total_leads = await Lead.find(Lead.user.id == current_user.id).count()
    leads_with_email = await Lead.find(
        Lead.user.id == current_user.id,
        Lead.contact_email != None
    ).count()
    
    # Get latest leads
    latest = await Lead.find(Lead.user.id == current_user.id).sort(-Lead.created_at).limit(5).to_list()
    
    return {
        "total_leads": total_leads,
        "leads_with_email": leads_with_email,
        "leads_without_email": total_leads - leads_with_email,
        "latest_leads": [
            {
                "company_name": lead.company_name,
                "created_at": lead.created_at.isoformat(),
                "has_email": bool(lead.contact_email),
                "status": lead.status
            }
            for lead in latest
        ],
        "user_settings": {
            "serpapi_configured": bool(current_user.serpapi_key),
            "hunter_configured": bool(current_user.hunter_api_key),
            "ai_provider": current_user.ai_provider,
            "google_sheets_enabled": current_user.google_sheets_enabled,
            "smtp_configured": bool(current_user.smtp_host and current_user.smtp_username)
        }
    }

@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific lead"""
    try:
        lead = await Lead.get(PydanticObjectId(lead_id))
    except:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Fix: Check ownership using Link field comparison (same as get_leads)
    if lead.user != current_user.id:
        raise HTTPException(status_code=403, detail="You don't have access to this lead")
    
    return LeadResponse(
        id=str(lead.id),
        company_name=lead.company_name,
        website=lead.website,
        industry=lead.industry,
        services=lead.services,
        contact_email=lead.contact_email,
        email_subject=lead.email_subject,
        email_body=lead.email_body,
        portfolio_path=lead.portfolio_path,
        status=lead.status,
        created_at=lead.created_at,
    )

@router.put("/{lead_id}")
async def update_lead(
    lead_id: str,
    request: UpdateLeadRequest,
    current_user: User = Depends(get_current_active_user),
):
    """Update a lead"""
    try:
        lead = await Lead.get(PydanticObjectId(lead_id))
    except:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Fix: Check ownership using Link field comparison
    if lead.user != current_user.id:
        raise HTTPException(status_code=403, detail="You don't have access to this lead")
    
    # Update fields
    update_data = request.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lead, field, value)
    
    lead.updated_at = datetime.utcnow()
    await lead.save()
    
    return {"message": "Lead updated successfully"}

@router.delete("/{lead_id}")
async def delete_lead(
    lead_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """Delete a lead"""
    try:
        lead = await Lead.get(PydanticObjectId(lead_id))
    except:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Fix: Check ownership using Link field comparison
    if lead.user != current_user.id:
        raise HTTPException(status_code=403, detail="You don't have access to this lead")
    
    await lead.delete()
    
    return {"message": "Lead deleted successfully"}

@router.post("/{lead_id}/send-email")
async def send_email_to_lead(
    lead_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
):
    """Send email to a specific lead"""
    from services.email_service import EmailService
    
    try:
        lead = await Lead.get(PydanticObjectId(lead_id))
    except:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Fix: Check ownership using Link field comparison
    if lead.user != current_user.id:
        raise HTTPException(status_code=403, detail="You don't have access to this lead")
    
    if not lead.contact_email:
        raise HTTPException(status_code=400, detail="Lead has no email address")
    
    # Send email directly (not in background for now to get immediate feedback)
    result = await EmailService.send_email(
        user=current_user,
        lead=lead
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to send email"))
    
    return result

@router.post("/send-all-emails")
async def send_emails_to_all_leads(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
):
    """Send emails to all leads that have email addresses"""
    from services.email_service import EmailService
    
    # Get all leads for this user that have email addresses
    leads = await Lead.find(
        Lead.user == current_user.id,
        Lead.contact_email != None,
        Lead.status != "contacted"  # Don't send to already contacted leads
    ).to_list()
    
    if not leads:
        raise HTTPException(status_code=400, detail="No leads found with email addresses to contact")
    
    sent_count = 0
    failed_count = 0
    results = []
    
    for lead in leads:
        try:
            result = await EmailService.send_email(
                user=current_user,
                lead=lead
            )
            
            if result["success"]:
                sent_count += 1
                # Update lead status to contacted
                lead.status = "contacted"
                await lead.save()
                results.append({
                    "lead_id": str(lead.id),
                    "company": lead.company_name,
                    "email": lead.contact_email,
                    "status": "sent"
                })
            else:
                failed_count += 1
                results.append({
                    "lead_id": str(lead.id),
                    "company": lead.company_name,
                    "email": lead.contact_email,
                    "status": "failed",
                    "error": result.get("error", "Unknown error")
                })
        except Exception as e:
            failed_count += 1
            results.append({
                "lead_id": str(lead.id),
                "company": lead.company_name,
                "email": lead.contact_email,
                "status": "failed",
                "error": str(e)
            })
    
    return {
        "message": f"Email sending completed. {sent_count} sent, {failed_count} failed",
        "total_leads": len(leads),
        "sent_count": sent_count,
        "failed_count": failed_count,
        "results": results
    }
