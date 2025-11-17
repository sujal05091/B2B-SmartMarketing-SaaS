"""Quick script to check which leads have emails"""
from src.core.sheets_manager import SheetsManager

sm = SheetsManager()
leads = sm.get_all_leads()

print("\n" + "="*70)
print("📊 LEADS WITH EMAIL ADDRESSES")
print("="*70)

for i, lead in enumerate(leads):
    company = lead.get('Company Name', 'Unknown')
    email = lead.get('Contact Email', '')
    
    if email:
        print(f"✅ Index {i}: {company}")
        print(f"   Email: {email}")
        print(f"   PDF: {lead.get('Portfolio File Path', 'None')}")
        print()

print("="*70)
print(f"Total leads: {len(leads)}")
print(f"Leads with email: {sum(1 for l in leads if l.get('Contact Email'))}")
print("="*70)
