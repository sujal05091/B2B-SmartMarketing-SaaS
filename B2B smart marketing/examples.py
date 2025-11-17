"""
Sample usage script demonstrating the Smart Marketing Assistant workflow.
This shows how to use the system programmatically (not just CLI).
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.web_analyzer import WebAnalyzer
from src.core.lead_discovery import LeadDiscovery
from src.core.ai_generator import AIGenerator
from src.core.portfolio_generator import PortfolioGenerator
from src.core.sheets_manager import SheetsManager
from src.utils.analytics import Analytics


def example_basic_workflow():
    """
    Example: Basic workflow for lead discovery.
    """
    print("\n" + "="*60)
    print(" 📝 EXAMPLE: Basic Workflow")
    print("="*60 + "\n")
    
    # Your business info
    your_business = {
        'name': 'TechSolutions Inc.',
        'description': 'We provide enterprise software development and cloud solutions',
        'url': 'https://techsolutions.example.com',
        'services': [
            'Custom Software Development',
            'Cloud Migration Services',
            'DevOps Consulting',
            'API Development',
            'Mobile App Development'
        ]
    }
    
    # Initialize components
    lead_discovery = LeadDiscovery()
    
    # Discover leads
    print("🔍 Discovering leads...")
    leads = lead_discovery.discover_leads(
        business_description=your_business['description'],
        services=your_business['services'],
        max_leads=5,
        region='USA',
        industry='Technology'
    )
    
    print(f"✅ Found {len(leads)} leads")
    for i, lead in enumerate(leads, 1):
        print(f"  {i}. {lead['company_name']} - {lead['website']}")


def example_analyze_website():
    """
    Example: Analyze a business website.
    """
    print("\n" + "="*60)
    print(" 📝 EXAMPLE: Website Analysis")
    print("="*60 + "\n")
    
    analyzer = WebAnalyzer()
    
    # Analyze website
    url = "https://example.com"
    print(f"📊 Analyzing: {url}")
    
    result = analyzer.analyze_website(url)
    
    if result.get('success'):
        print(f"\n✅ Analysis Complete:")
        print(f"  Title: {result['title']}")
        print(f"  Industry: {result['industry']}")
        print(f"  Services Found: {len(result['services'])}")
        for service in result['services'][:5]:
            print(f"    • {service}")
    else:
        print(f"❌ Error: {result.get('error')}")


def example_generate_email():
    """
    Example: Generate personalized email.
    """
    print("\n" + "="*60)
    print(" 📝 EXAMPLE: Email Generation")
    print("="*60 + "\n")
    
    ai_generator = AIGenerator()
    
    your_business = {
        'name': 'Marketing Pro',
        'description': 'Digital marketing and SEO services',
        'services': ['SEO Optimization', 'Social Media Marketing', 'Content Marketing']
    }
    
    lead = {
        'company_name': 'Example Corp',
        'website': 'https://example.com',
        'industry': 'E-commerce',
        'description': 'Online retail platform'
    }
    
    matched_services = ['SEO Optimization', 'Social Media Marketing']
    
    print("✉️  Generating personalized email...")
    
    email = ai_generator.generate_outreach_email(
        your_business,
        lead,
        matched_services,
        tone='professional'
    )
    
    if email.get('success'):
        print(f"\n✅ Email Generated:")
        print(f"\nSubject: {email['subject']}")
        print(f"\n{email['body'][:200]}...")
    else:
        print(f"❌ Error: {email.get('error')}")


def example_create_portfolio():
    """
    Example: Create PDF portfolio.
    """
    print("\n" + "="*60)
    print(" 📝 EXAMPLE: Portfolio Generation")
    print("="*60 + "\n")
    
    portfolio_gen = PortfolioGenerator()
    
    your_business = {
        'name': 'Design Studio',
        'description': 'Creative design and branding services',
        'url': 'https://designstudio.example.com',
        'contact_email': 'hello@designstudio.com'
    }
    
    lead = {
        'company_name': 'Fashion Brand Co.',
        'industry': 'Fashion',
        'website': 'https://fashionbrand.com'
    }
    
    matched_services = [
        'Brand Identity Design',
        'Website Design',
        'Social Media Graphics'
    ]
    
    email_content = {
        'subject': 'Partnership Opportunity',
        'body': 'Sample email body...'
    }
    
    print("📁 Creating PDF portfolio...")
    
    result = portfolio_gen.generate_portfolio(
        your_business,
        lead,
        matched_services,
        email_content
    )
    
    if result.get('success'):
        print(f"\n✅ Portfolio Created:")
        print(f"  File: {result['file_name']}")
        print(f"  Path: {result['file_path']}")
    else:
        print(f"❌ Error: {result.get('error')}")


def example_analytics():
    """
    Example: View analytics.
    """
    print("\n" + "="*60)
    print(" 📝 EXAMPLE: Analytics Dashboard")
    print("="*60 + "\n")
    
    analytics = Analytics()
    
    # Get summary
    summary = analytics.get_summary()
    
    print("📊 Analytics Summary:")
    print(f"  Total Runs: {summary['total_runs']}")
    print(f"  Total Leads: {summary['total_leads']}")
    print(f"  Total Emails: {summary['total_emails']}")
    print(f"  Success Rate: {summary['success_rate']}%")
    
    if summary['top_industries']:
        print(f"\n  Top Industries:")
        for industry, count in summary['top_industries']:
            print(f"    • {industry}: {count}")


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print(" 🚀 SMART MARKETING ASSISTANT - USAGE EXAMPLES")
    print("="*70)
    
    examples = [
        ("Basic Workflow", example_basic_workflow),
        ("Website Analysis", example_analyze_website),
        ("Email Generation", example_generate_email),
        ("Portfolio Creation", example_create_portfolio),
        ("Analytics", example_analytics)
    ]
    
    print("\nAvailable Examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print("\nNote: These are demonstrations of the API.")
    print("For actual usage, ensure your .env is configured properly.")
    print("\nTo run the full workflow, use:")
    print("  python cli.py --name 'Company' --desc 'Description' --url 'https://example.com'")
    
    # Uncomment to run specific examples:
    # example_basic_workflow()
    # example_analyze_website()
    # example_generate_email()
    # example_create_portfolio()
    # example_analytics()


if __name__ == "__main__":
    main()
