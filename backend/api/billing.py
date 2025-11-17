from fastapi import APIRouter, Depends, Request, HTTPException
from core.security import get_current_active_user
from models.user import User
import os
import json

router = APIRouter()

# Stripe configuration
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_...")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "pk_test_...")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_...")

try:
    import stripe
    stripe.api_key = STRIPE_SECRET_KEY
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False

router = APIRouter()

@router.get("/plans")
async def get_pricing_plans():
    """Get available pricing plans"""
    return {
        "plans": [
            {
                "name": "Free",
                "price": 0,
                "lead_limit": 50,
                "features": ["50 leads/month", "AI email generation", "PDF portfolios"],
            },
            {
                "name": "Pro",
                "price": 9.99,
                "lead_limit": 500,
                "features": ["500 leads/month", "Email sending", "API access", "Priority support"],
            },
            {
                "name": "Enterprise",
                "price": 29.99,
                "lead_limit": 999999,
                "features": ["Unlimited leads", "White-label", "Phone support", "Custom integrations"],
            }
        ]
    }

@router.post("/create-checkout-session")
async def create_checkout_session(
    request: dict,
    current_user: User = Depends(get_current_active_user)
):
    """Create Stripe checkout session"""
    if not STRIPE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Payment system not configured")
    
    price_id = request.get("priceId")
    billing_cycle = request.get("billingCycle", "monthly")
    
    if not price_id:
        raise HTTPException(status_code=400, detail="Price ID required")
    
    try:
        # Map plan names to price IDs (these would be real Stripe price IDs)
        price_mapping = {
            "price_pro_monthly": "price_pro_monthly",
            "price_enterprise_monthly": "price_enterprise_monthly",
            "price_pro_yearly": "price_pro_yearly",
            "price_enterprise_yearly": "price_enterprise_yearly"
        }
        
        if price_id not in price_mapping:
            raise HTTPException(status_code=400, detail="Invalid price ID")
        
        checkout_session = stripe.checkout.Session.create(
            customer_email=current_user.email,
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f"http://localhost:3000/dashboard?success=true",
            cancel_url=f"http://localhost:3000/pricing?canceled=true",
            metadata={
                'user_id': str(current_user.id),
                'plan_type': 'subscription'
            }
        )
        
        return {"url": checkout_session.url}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create checkout session: {str(e)}")

@router.post("/buy-leads")
async def buy_leads(
    request: dict,
    current_user: User = Depends(get_current_active_user)
):
    """Buy additional leads (one-time purchase)"""
    if not STRIPE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Payment system not configured")
    
    lead_pack = request.get("leadPack", 100)
    price = request.get("price", 4.99)
    
    try:
        checkout_session = stripe.checkout.Session.create(
            customer_email=current_user.email,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'{lead_pack} Additional Leads',
                        'description': f'Purchase {lead_pack} additional leads for your account',
                    },
                    'unit_amount': int(price * 100),  # Convert to cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"http://localhost:3000/dashboard?leads_added={lead_pack}",
            cancel_url=f"http://localhost:3000/pricing?canceled=true",
            metadata={
                'user_id': str(current_user.id),
                'lead_pack': str(lead_pack),
                'plan_type': 'one_time_leads'
            }
        )
        
        return {"url": checkout_session.url}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create lead purchase session: {str(e)}")

@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    if not STRIPE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Payment system not configured")
    
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        # Verify webhook signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        await handle_checkout_completed(session)
    elif event['type'] == 'invoice.payment_succeeded':
        invoice = event['data']['object']
        await handle_payment_succeeded(invoice)
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        await handle_subscription_cancelled(subscription)
    
    return {"status": "success"}

async def handle_checkout_completed(session):
    """Handle successful checkout completion"""
    user_id = session.metadata.get('user_id')
    plan_type = session.metadata.get('plan_type')
    
    if not user_id:
        return
    
    user = await User.get(user_id)
    if not user:
        return
    
    if plan_type == 'subscription':
        # Update user plan and limits
        if 'pro' in session.metadata.get('price_id', '').lower():
            user.plan = 'pro'
            user.lead_limit = 500
        elif 'enterprise' in session.metadata.get('price_id', '').lower():
            user.plan = 'enterprise'
            user.lead_limit = 999999
        
        await user.save()
    
    elif plan_type == 'one_time_leads':
        # Add leads to user's limit
        lead_pack = int(session.metadata.get('lead_pack', 100))
        user.lead_limit += lead_pack
        await user.save()

async def handle_payment_succeeded(invoice):
    """Handle successful payment for subscriptions"""
    customer_id = invoice.get('customer')
    if customer_id:
        # Find user by stripe customer ID and ensure subscription is active
        user = await User.find_one(User.stripe_customer_id == customer_id)
        if user:
            # Ensure user has the correct plan limits
            if user.plan == 'pro':
                user.lead_limit = 500
            elif user.plan == 'enterprise':
                user.lead_limit = 999999
            await user.save()

async def handle_subscription_cancelled(subscription):
    """Handle subscription cancellation"""
    customer_id = subscription.get('customer')
    if customer_id:
        user = await User.find_one(User.stripe_customer_id == customer_id)
        if user:
            # Downgrade to free plan
            user.plan = 'free'
            user.lead_limit = 50
            await user.save()

@router.post("/reset-usage")
async def reset_monthly_usage(current_user: User = Depends(get_current_active_user)):
    """Reset monthly lead usage (for testing/admin)"""
    if current_user.is_admin:
        # Reset all users' leads_used to 0
        await User.find_all().update({"$set": {"leads_used": 0}})
        return {"message": "Monthly usage reset for all users"}
    else:
        # Reset only current user's usage
        current_user.leads_used = 0
        await current_user.save()
        return {"message": "Your monthly usage has been reset"}
