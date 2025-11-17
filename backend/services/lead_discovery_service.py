"""
Service that integrates real lead discovery with SerpAPI and Hunter.io
"""
import sys
import os
from pathlib import Path
from typing import List, Dict

from models.user import User
from models.lead import Lead
from models.usage import UsageTracking
from services.search_service import SearchService
from services.ai_service import AIService
from services.google_sheets_service import GoogleSheetsService
from beanie import Link
from datetime import datetime
import asyncio

async def discover_leads_task(task_id: str, user_id: str, request_data: dict):
    """
    Background task to discover leads using real APIs (SerpAPI + Hunter.io)
    Saves results to MongoDB and optionally to Google Sheets
    """
    try:
        print(f"🚀 Starting lead discovery task: {task_id}")
        print(f"   User ID: {user_id}")
        
        # Get user
        user = await User.get(user_id)
        if not user:
            print(f"❌ User not found: {user_id}")
            return
        
        # Prepare parameters
        industry = request_data.get('target_industry', 'businesses')
        region = request_data.get('target_region', 'United States')
        max_leads = request_data.get('max_leads', 10)
        
        print(f"📊 Discovering leads for {industry} in {region}")
        
        # Check if SerpAPI is configured
        if not user.serpapi_key:
            print(f"⚠️ SerpAPI not configured, creating demo leads")
            await _create_demo_leads(user, request_data, task_id)
            return
        
        # Search for businesses
        businesses = await SearchService.search_businesses(
            user=user,
            industry=industry,
            location=region,
            limit=max_leads
        )
        
        if isinstance(businesses, dict) and "error" in businesses:
            print(f"❌ Search failed: {businesses['error']}")
            print(f"⚠️ Falling back to demo leads")
            await _create_demo_leads(user, request_data, task_id)
            return
        
        if not businesses:
            print(f"⚠️ No businesses found, creating demo leads")
            await _create_demo_leads(user, request_data, task_id)
            return
        
        print(f"✅ Found {len(businesses)} businesses")
        
        # Process each business
        saved_count = 0
        leads_to_export = []
        
        for business_data in businesses:
            try:
                company_name = business_data.get('company_name', 'Unknown')
                website = business_data.get('website', '')
                description = business_data.get('description', '')
                
                # Find email if Hunter.io is configured
                contact_email = None
                if website and user.hunter_api_key:
                    contact_email = await SearchService.find_email(
                        user=user,
                        domain=website,
                        company_name=company_name
                    )
                
                # Generate personalized email using AI
                email_data = await AIService.generate_email(
                    user=user,
                    company_name=company_name,
                    industry=industry,
                    description=description
                )
                
                # Create Lead document
                lead = Lead(
                    user=Link(user.id, User),
                    company_name=company_name,
                    website=website,
                    industry=industry,
                    services=description[:500] if description else f"Services in {industry}",
                    contact_email=contact_email,
                    email_subject=email_data.get('subject', ''),
                    email_body=email_data.get('body', ''),
                    status='new',
                    created_at=datetime.utcnow(),
                )
                
                await lead.insert()
                saved_count += 1
                leads_to_export.append(lead)
                print(f"   💾 Saved: {company_name} {f'({contact_email})' if contact_email else ''}")
                
                # Increment user's leads_used counter
                user.leads_used += 1
                await user.save()
                
            except Exception as e:
                print(f"   ❌ Error saving lead: {str(e)}")
                continue
        
        print(f"✅ Saved {saved_count} leads to database")
        
        # Export to Google Sheets if enabled
        if user.google_sheets_enabled and leads_to_export:
            try:
                print(f"📊 Attempting to export {len(leads_to_export)} leads to Google Sheets...")
                result = await GoogleSheetsService.export_leads(user, leads_to_export)
                if result.get('success'):
                    print(f"✅ Exported to Google Sheets: {result.get('sheet_url')}")
                else:
                    print(f"❌ Google Sheets export failed: {result.get('error')}")
            except Exception as e:
                print(f"❌ Google Sheets export error: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Update usage tracking
        usage = await UsageTracking.find_one(UsageTracking.user.id == user.id)
        if usage:
            usage.total_leads += saved_count
            usage.updated_at = datetime.utcnow()
            await usage.save()
            print(f"📊 Updated usage: +{saved_count} leads")
        
    except Exception as e:
        print(f"❌ Task failed: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print(f"🏁 Lead discovery task completed: {task_id}")

async def _create_demo_leads(user: User, request_data: dict, task_id: str):
    """Create demo leads for testing when discovery fails"""
    print(f"Creating demo leads for testing...")
    print(f"   User info: ID={user.id}, Email={user.email}")
    
    industry = request_data.get('target_industry', 'businesses')
    region = request_data.get('target_region', 'Global')
    max_leads = min(request_data.get('max_leads', 5), 5)  # Max 5 demo leads
    
    demo_leads = [
        {
            "company_name": f"Demo {industry.title()} Company 1",
            "website": f"https://demo{industry}1.com",
            "contact_email": f"contact@demo{industry}1.com",
            "industry": industry,
            "region": region,
        },
        {
            "company_name": f"Sample {industry.title()} Business 2",
            "website": f"https://sample{industry}2.com",
            "contact_email": f"info@sample{industry}2.com",
            "industry": industry,
            "region": region,
        },
        {
            "company_name": f"Test {industry.title()} Corp 3",
            "website": f"https://test{industry}3.com",
            "contact_email": f"hello@test{industry}3.com",
            "industry": industry,
            "region": region,
        },
    ]
    
    saved_count = 0
    for i, lead_data in enumerate(demo_leads[:max_leads]):
        try:
            lead = Lead(
                user=Link(user.id, User),  # Use Link with just the ID
                company_name=lead_data['company_name'],
                website=lead_data['website'],
                industry=lead_data['industry'],
                services=f"Services in {industry}",
                contact_email=lead_data['contact_email'],
                email_subject=f"Partnership Opportunity with {user.company_name}",
                email_body=f"Hi, We noticed your company {lead_data['company_name']} and think there could be great partnership opportunities...",
                status='new',
                created_at=datetime.utcnow(),
            )
            
            print(f"   📝 Lead user link: {lead.user}")
            await lead.insert()
            saved_count += 1
            print(f"   💾 Created demo lead: {lead.company_name}")
            
            # Increment user's leads_used counter
            user.leads_used += 1
            await user.save()
            
        except Exception as e:
            print(f"   ⚠️  Failed to create demo lead: {e}")
            continue
    
    print(f"✅ Created {saved_count} demo leads for testing")
    
    # Export to Google Sheets if enabled
    if user.google_sheets_enabled and saved_count > 0:
        try:
            print(f"📊 Attempting to export {saved_count} demo leads to Google Sheets...")
            # Get the leads we just created
            demo_leads = await Lead.find(Lead.user.id == user.id).sort(-Lead.created_at).limit(saved_count).to_list()
            result = await GoogleSheetsService.export_leads(user, demo_leads)
            if result.get('success'):
                print(f"✅ Exported demo leads to Google Sheets: {result.get('sheet_url')}")
            else:
                print(f"❌ Google Sheets export failed: {result.get('error')}")
        except Exception as e:
            print(f"❌ Google Sheets export error: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Update usage tracking
    usage = await UsageTracking.find_one(UsageTracking.user.id == user.id)
    if usage:
        usage.total_leads += saved_count
        usage.updated_at = datetime.utcnow()
        await usage.save()
        print(f"📊 Updated usage: +{saved_count} leads")
