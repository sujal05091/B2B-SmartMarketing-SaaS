"""
Smart Marketing Assistant - Command Line Interface

Main entry point for the Smart Marketing Assistant application.
Handles command-line arguments and orchestrates the entire workflow.
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.web_analyzer import WebAnalyzer
from src.core.lead_discovery import LeadDiscovery
from src.core.ai_generator import AIGenerator
from src.core.portfolio_generator import PortfolioGenerator
from src.core.sheets_manager import SheetsManager
from src.utils.logger import setup_logger, get_logger
from src.utils.config import get_config
from src.utils.analytics import Analytics
from src.utils.email_sender import EmailSender


class SmartMarketingAssistant:
    """
    Main application class that orchestrates the entire workflow.
    
    Workflow:
    1. Analyze your business website
    2. Discover potential leads
    3. Analyze each lead's website
    4. Generate personalized emails
    5. Create PDF portfolios
    6. Update Google Sheets
    7. Track analytics
    """
    
    def __init__(self):
        """Initialize the Smart Marketing Assistant."""
        self.config = get_config()
        self.logger = setup_logger("SmartMarketingAssistant", self.config.LOG_LEVEL)
        
        # Initialize components
        self.web_analyzer = WebAnalyzer()
        self.lead_discovery = LeadDiscovery()
        self.ai_generator = AIGenerator()
        self.portfolio_generator = PortfolioGenerator()
        self.sheets_manager = SheetsManager()
        self.analytics = Analytics()
        
        self.logger.info("Smart Marketing Assistant initialized")
    
    def run(self, business_name: str, business_desc: str, business_url: str,
            max_leads: int = 10, region: Optional[str] = None,
            industry: Optional[str] = None) -> dict:
        """
        Run the complete marketing automation workflow.
        
        Args:
            business_name: Your business name
            business_desc: Your business description
            business_url: Your business website URL
            max_leads: Maximum number of leads to discover
            region: Target region (optional)
            industry: Target industry (optional)
        
        Returns:
            Dictionary with execution results
        """
        self.logger.info(f"Starting workflow for: {business_name}")
        
        try:
            # Step 1: Analyze your business website
            print("\n📊 Analyzing your business website...")
            your_business_data = self.web_analyzer.analyze_website(business_url)
            
            if not your_business_data.get('success'):
                self.logger.error("Failed to analyze business website")
                print("❌ Error: Could not analyze your website. Please check the URL.")
                return {'success': False, 'error': 'Website analysis failed'}
            
            your_business = {
                'name': business_name,
                'description': business_desc,
                'url': business_url,
                'services': your_business_data.get('services', []),
                'industry': your_business_data.get('industry', 'General Business'),
                'contact_email': your_business_data.get('contact_email', ''),
                'keywords': your_business_data.get('keywords', [])
            }
            
            print(f"✅ Found {len(your_business['services'])} services")
            
            # Step 2: Discover leads
            print(f"\n🔍 Discovering potential leads (max: {max_leads})...")
            leads = self.lead_discovery.discover_leads(
                business_desc,
                your_business['services'],
                max_leads=max_leads,
                region=region,
                industry=industry
            )
            
            if not leads:
                self.logger.warning("No leads discovered")
                print("⚠️  No leads found. Try adjusting your search criteria.")
                return {'success': False, 'error': 'No leads found'}
            
            print(f"✅ Discovered {len(leads)} potential leads")
            
            # Step 3-6: Process each lead
            results = {
                'total_leads': len(leads),
                'processed': 0,
                'emails_generated': 0,
                'portfolios_created': 0,
                'duplicates': 0,
                'errors': 0,
                'industries': []
            }
            
            print(f"\n🚀 Processing leads...")
            
            for i, lead in enumerate(leads, 1):
                print(f"\n[{i}/{len(leads)}] Processing: {lead['company_name']}")
                
                try:
                    # Step 3: Enrich with contact email (Hunter.io)
                    print("  📧 Finding contact email...")
                    lead = self.lead_discovery.enrich_lead_contacts(lead)
                    contact_email = ''
                    if lead.get('contacts') and len(lead['contacts']) > 0:
                        contact_email = lead['contacts'][0].get('email', '')
                        print(f"  ✅ Found: {contact_email}")
                    else:
                        print("  ⚠️  No email found")
                    
                    # Step 4: Analyze lead's website
                    print("  📄 Analyzing website...")
                    lead_analysis = self.web_analyzer.analyze_website(lead['website'])
                    
                    if lead_analysis.get('success'):
                        lead['industry'] = lead_analysis.get('industry', lead.get('industry', 'Unknown'))
                        lead['description'] = lead_analysis.get('description', lead.get('description', ''))
                        website_content = lead_analysis.get('main_content', '')
                    else:
                        website_content = lead.get('description', '')
                    
                    # Track industry
                    if lead['industry'] not in results['industries']:
                        results['industries'].append(lead['industry'])
                    
                    # Step 4: Match services
                    print("  🎯 Matching services...")
                    matched_services = self.ai_generator.match_services_to_lead(
                        your_business['services'],
                        lead,
                        website_content
                    )
                    
                    # Step 5: Generate email
                    print("  ✉️  Generating personalized email...")
                    email_content = self.ai_generator.generate_outreach_email(
                        your_business,
                        lead,
                        matched_services
                    )
                    
                    if email_content.get('success'):
                        results['emails_generated'] += 1
                    
                    # Step 6: Create portfolio
                    print("  📁 Creating PDF portfolio...")
                    portfolio_result = self.portfolio_generator.generate_portfolio(
                        your_business,
                        lead,
                        matched_services,
                        email_content
                    )
                    
                    if portfolio_result.get('success'):
                        results['portfolios_created'] += 1
                    
                    # Step 7: Add to Google Sheets
                    print("  📊 Updating Google Sheets...")
                    sheet_data = {
                        'company_name': lead['company_name'],
                        'website': lead['website'],
                        'contact_email': contact_email,
                        'industry': lead['industry'],
                        'matched_services': matched_services,
                        'email_subject': email_content.get('subject', ''),
                        'email_body': email_content.get('body', ''),
                        'portfolio_path': portfolio_result.get('file_path', '')
                    }
                    
                    sheet_result = self.sheets_manager.add_lead(sheet_data)
                    
                    if sheet_result.get('is_duplicate'):
                        print("  ⚠️  Duplicate - skipped")
                        results['duplicates'] += 1
                    elif sheet_result.get('success'):
                        print("  ✅ Added to Google Sheets")
                        results['processed'] += 1
                    else:
                        print(f"  ❌ Error adding to sheets: {sheet_result.get('error', 'Unknown')}")
                        results['errors'] += 1
                    
                except Exception as e:
                    self.logger.error(f"Error processing lead {lead['company_name']}: {e}", exc_info=True)
                    print(f"  ❌ Error: {str(e)}")
                    results['errors'] += 1
            
            # Step 8: Record analytics
            self.analytics.record_run(
                business_name=business_name,
                leads_found=results['total_leads'],
                emails_generated=results['emails_generated'],
                portfolios_created=results['portfolios_created'],
                duplicates=results['duplicates'],
                industries=results['industries'],
                success=True
            )
            
            # Print summary
            self._print_summary(results)
            
            self.logger.info("Workflow completed successfully")
            return {'success': True, 'results': results}
            
        except Exception as e:
            self.logger.error(f"Workflow error: {e}", exc_info=True)
            print(f"\n❌ Error: {str(e)}")
            
            # Record failed run
            self.analytics.record_run(
                business_name=business_name,
                leads_found=0,
                emails_generated=0,
                portfolios_created=0,
                duplicates=0,
                industries=[],
                success=False,
                error=str(e)
            )
            
            return {'success': False, 'error': str(e)}
    
    def _print_summary(self, results: dict):
        """Print execution summary."""
        print("\n" + "="*60)
        print(" 📊 EXECUTION SUMMARY")
        print("="*60)
        print(f"Total Leads Discovered: {results['total_leads']}")
        print(f"Successfully Processed: {results['processed']}")
        print(f"Emails Generated: {results['emails_generated']}")
        print(f"Portfolios Created: {results['portfolios_created']}")
        print(f"Duplicates Skipped: {results['duplicates']}")
        print(f"Errors: {results['errors']}")
        print(f"Unique Industries: {len(results['industries'])}")
        if results['industries']:
            print(f"Industries Found: {', '.join(results['industries'])}")
        print("="*60)


def handle_test_email():
    """Test email configuration."""
    print("\n🧪 Testing email configuration...\n")
    
    try:
        email_sender = EmailSender()
        
        # Test SMTP connection
        print("Testing SMTP connection...")
        test_result = email_sender.send_email(
            recipient_email=email_sender.sender_email,
            subject="✅ Test Email - Smart Marketing Assistant",
            body="""This is a test email from your B2B Smart Marketing Assistant.

If you received this email, your SMTP configuration is working correctly!

Configuration Details:
- SMTP Host: {}
- SMTP Port: {}
- Sender Email: {}
- Sender Name: {}

You can now send automated B2B outreach emails to your leads!

Best regards,
Smart Marketing Assistant
""".format(
                email_sender.smtp_host,
                email_sender.smtp_port,
                email_sender.sender_email,
                email_sender.sender_name
            )
        )
        
        if test_result['success']:
            print(f"✅ Test email sent successfully to {email_sender.sender_email}")
            print("\n📧 Check your inbox!")
            print(f"   SMTP Host: {email_sender.smtp_host}:{email_sender.smtp_port}")
            print(f"   Sender: {email_sender.sender_name} <{email_sender.sender_email}>")
        else:
            print(f"❌ Failed to send test email: {test_result['error']}")
            print("\nPlease check your .env file SMTP configuration:")
            print("  - SMTP_HOST")
            print("  - SMTP_PORT")
            print("  - SMTP_USERNAME")
            print("  - SMTP_PASSWORD")
            print("  - SENDER_EMAIL")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nPlease verify your email configuration in .env file")


def handle_send_single_email(lead_index: int):
    """Send email to a specific lead."""
    print(f"\n📧 Sending email to lead #{lead_index}...\n")
    
    try:
        sheets_manager = SheetsManager()
        email_sender = EmailSender()
        
        # Get all leads
        print("📊 Fetching leads from Google Sheets...")
        leads = sheets_manager.get_all_leads()
        
        if not leads:
            print("❌ No leads found in Google Sheets")
            return
        
        if lead_index >= len(leads):
            print(f"❌ Error: Lead index {lead_index} out of range")
            print(f"   Available range: 0 to {len(leads)-1}")
            return
        
        lead = leads[lead_index]
        
        # Check if lead has required data
        contact_email = lead.get('Contact Email', '').strip()
        if not contact_email:
            print(f"❌ Error: No email found for {lead.get('Company Name', 'this lead')}")
            print("   Hunter.io may not have found an email for this company")
            return
        
        # Check if already sent
        if lead.get('status') == 'Sent':
            print(f"⚠️  Email already sent to {lead['company_name']}")
            response = input("   Send anyway? (y/n): ")
            if response.lower() != 'y':
                print("   Cancelled")
                return
        
        print(f"📤 Sending to: {lead.get('Company Name', 'Unknown')}")
        print(f"   Email: {contact_email}")
        print(f"   Subject: {lead.get('Email Subject', 'Partnership Opportunity')}")
        
        # Get PDF path
        pdf_path = lead.get('Portfolio File Path', '') or lead.get('portfolio_path', '')
        if pdf_path and os.path.exists(pdf_path):
            print(f"   📎 Attaching: {Path(pdf_path).name}")
        else:
            pdf_path = None
            print(f"   ⚠️  No PDF portfolio found")
        
        # Send email with PDF attachment
        result = email_sender.send_email(
            recipient_email=contact_email,
            subject=lead.get('Email Subject', 'Partnership Opportunity'),
            body=lead.get('Email Body', ''),
            attachment_path=pdf_path
        )
        
        if result['success']:
            # Update status in sheets
            sheets_manager.update_lead_status(lead.get('Website', ''), 'Sent')
            print(f"\n✅ Email sent successfully!")
            if pdf_path:
                print(f"   📎 PDF portfolio attached")
            print(f"   📊 Status updated in Google Sheets")
        else:
            print(f"\n❌ Failed to send email: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def handle_send_all_emails():
    """Send emails to all unsent leads."""
    print("\n📧 Sending emails to all unsent leads...\n")
    
    try:
        sheets_manager = SheetsManager()
        email_sender = EmailSender()
        
        # Get all leads
        print("📊 Fetching leads from Google Sheets...")
        leads = sheets_manager.get_all_leads()
        
        if not leads:
            print("❌ No leads found in Google Sheets")
            return
        
        # Filter unsent leads with emails
        unsent_leads = [
            lead for lead in leads 
            if lead.get('Status') != 'Sent' and lead.get('Contact Email', '').strip()
        ]
        
        if not unsent_leads:
            print("✅ All leads with emails have already been contacted!")
            return
        
        print(f"Found {len(unsent_leads)} unsent leads with emails")
        print("\nLeads to contact:")
        for i, lead in enumerate(unsent_leads, 1):
            print(f"  {i}. {lead.get('Company Name', 'Unknown')} ({lead.get('Contact Email', 'No email')})")
        
        # Confirm before sending
        print(f"\n⚠️  About to send {len(unsent_leads)} emails")
        response = input("Continue? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled")
            return
        
        # Send emails
        sent_count = 0
        failed_count = 0
        
        print("\n" + "="*60)
        for i, lead in enumerate(unsent_leads, 1):
            contact_email = lead.get('Contact Email', '').strip()
            print(f"\n[{i}/{len(unsent_leads)}] {lead.get('Company Name', 'Unknown')}")
            print(f"   Email: {contact_email}")
            
            # Get PDF path
            pdf_path = lead.get('Portfolio File Path', '') or lead.get('portfolio_path', '')
            if pdf_path and os.path.exists(pdf_path):
                print(f"   📎 Attaching: {Path(pdf_path).name}")
            else:
                pdf_path = None
            
            result = email_sender.send_email(
                recipient_email=contact_email,
                subject=lead.get('Email Subject', 'Partnership Opportunity'),
                body=lead.get('Email Body', ''),
                attachment_path=pdf_path
            )
            
            if result['success']:
                sheets_manager.update_lead_status(lead.get('Website', ''), 'Sent')
                if pdf_path:
                    print(f"   ✅ Sent with PDF!")
                else:
                    print(f"   ✅ Sent!")
                sent_count += 1
            else:
                print(f"   ❌ Failed: {result['error']}")
                failed_count += 1
            
            # Rate limiting (2 seconds between emails)
            if i < len(unsent_leads):
                import time
                time.sleep(2)
        
        # Summary
        print("\n" + "="*60)
        print("📊 Email Sending Summary:")
        print(f"   ✅ Sent: {sent_count}")
        print(f"   ❌ Failed: {failed_count}")
        print(f"   📊 Total: {len(unsent_leads)}")
        print("="*60)
        print("\n✅ Batch sending complete!")
        print("📊 Check Google Sheets for updated status")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Smart Marketing Assistant - AI-powered B2B lead discovery and outreach automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py --name "AdVision Marketing" --desc "Digital Marketing & SEO Agency" --url "https://advision.com"
  
  python cli.py --name "TechCorp" --desc "Software Development" --url "https://techcorp.com" --max-leads 20 --region "North America"
  
  python cli.py --analytics  # View analytics summary
  
  python cli.py --validate   # Validate configuration
        """
    )
    
    # Main arguments
    parser.add_argument('--name', type=str, help='Your business name')
    parser.add_argument('--desc', type=str, help='Your business description')
    parser.add_argument('--url', type=str, help='Your business website URL')
    
    # Optional arguments
    parser.add_argument('--max-leads', type=int, default=10,
                       help='Maximum number of leads to discover (default: 10)')
    parser.add_argument('--region', type=str,
                       help='Target geographic region (e.g., "North America", "Europe")')
    parser.add_argument('--industry', type=str,
                       help='Target industry (e.g., "Technology", "Healthcare")')
    
    # Special modes
    parser.add_argument('--analytics', action='store_true',
                       help='Display analytics summary')
    parser.add_argument('--validate', action='store_true',
                       help='Validate configuration')
    parser.add_argument('--version', action='version', version='Smart Marketing Assistant 1.0.0')
    
    # Email sending arguments
    parser.add_argument('--test-email', action='store_true',
                       help='Test SMTP email configuration')
    parser.add_argument('--send-email', action='store_true',
                       help='Send email to a specific lead')
    parser.add_argument('--lead-index', type=int,
                       help='Lead row index to send email to (0-based)')
    parser.add_argument('--send-all-emails', action='store_true',
                       help='Send emails to all unsent leads')
    
    args = parser.parse_args()
    
    # Handle email testing
    if args.test_email:
        handle_test_email()
        return
    
    # Handle single email sending
    if args.send_email:
        if args.lead_index is None:
            print("❌ Error: --lead-index required with --send-email")
            print("Example: python cli.py --send-email --lead-index 0")
            sys.exit(1)
        handle_send_single_email(args.lead_index)
        return
    
    # Handle batch email sending
    if args.send_all_emails:
        handle_send_all_emails()
        return
    
    # Handle special modes
    if args.analytics:
        analytics = Analytics()
        analytics.print_summary()
        return
    
    if args.validate:
        print("\n🔍 Validating configuration...")
        config = get_config()
        is_valid, missing = config.validate()
        
        if is_valid:
            print("✅ Configuration is valid!")
            summary = config.get_config_summary()
            print("\nConfiguration Summary:")
            for key, value in summary.items():
                print(f"  • {key}: {value}")
        else:
            print("❌ Configuration is incomplete!")
            print("\nMissing:")
            for item in missing:
                print(f"  • {item}")
            print("\nPlease update your .env file with the required values.")
            sys.exit(1)
        return
    
    # Validate required arguments
    if not all([args.name, args.desc, args.url]):
        parser.print_help()
        print("\n❌ Error: --name, --desc, and --url are required arguments")
        sys.exit(1)
    
    # Validate configuration
    config = get_config()
    is_valid, missing = config.validate()
    
    if not is_valid:
        print("❌ Configuration Error: Missing required settings")
        print("\nMissing:")
        for item in missing:
            print(f"  • {item}")
        print("\nPlease update your .env file. Use .env.example as a template.")
        sys.exit(1)
    
    # Print welcome message
    print("\n" + "="*60)
    print(" 🚀 SMART MARKETING ASSISTANT")
    print("="*60)
    print(f"Business: {args.name}")
    print(f"Target Leads: {args.max_leads}")
    if args.region:
        print(f"Region: {args.region}")
    if args.industry:
        print(f"Industry: {args.industry}")
    print("="*60)
    
    # Run the assistant
    try:
        assistant = SmartMarketingAssistant()
        result = assistant.run(
            business_name=args.name,
            business_desc=args.desc,
            business_url=args.url,
            max_leads=args.max_leads,
            region=args.region,
            industry=args.industry
        )
        
        if result['success']:
            print("\n✅ Workflow completed successfully!")
            print(f"📁 Portfolios saved to: {config.PORTFOLIO_DIR}")
            print(f"📊 Data recorded in Google Sheets")
            print(f"📝 Logs available at: logs/activity.log")
        else:
            print("\n❌ Workflow failed. Check logs for details.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        print("Check logs/activity.log for details")
        sys.exit(1)


if __name__ == "__main__":
    main()
