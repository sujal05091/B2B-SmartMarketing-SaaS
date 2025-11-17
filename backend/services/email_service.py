import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from models.user import User
from models.lead import Lead
from models.usage import UsageTracking
from datetime import datetime

class EmailService:
    """Service for sending emails via SMTP"""
    
    @staticmethod
    async def send_email(
        user: User,
        lead: Lead,
        subject: Optional[str] = None,
        body: Optional[str] = None,
    ) -> dict:
        """
        Send an email to a lead using the user's SMTP settings
        
        Args:
            user: User object with SMTP configuration
            lead: Lead object to send email to
            subject: Optional email subject (uses lead.email_subject if not provided)
            body: Optional email body (uses lead.email_body if not provided)
            
        Returns:
            dict with success status and message
        """
        # Validate SMTP configuration
        if not all([user.smtp_host, user.smtp_port, user.smtp_username, 
                   user.smtp_password, user.smtp_from_email]):
            return {
                "success": False,
                "error": "SMTP not configured. Please configure SMTP settings first."
            }
        
        # Validate lead has email
        if not lead.contact_email:
            return {
                "success": False,
                "error": "Lead has no email address"
            }
        
        # Use provided subject/body or lead's default
        email_subject = subject or lead.email_subject or f"Partnership Opportunity with {user.company_name}"
        email_body = body or lead.email_body or "Hello, we'd like to discuss a partnership opportunity."
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = email_subject
            msg['From'] = f"{user.smtp_from_name or user.full_name} <{user.smtp_from_email}>"
            msg['To'] = lead.contact_email
            
            # Add plain text and HTML versions
            text_part = MIMEText(email_body, 'plain')
            html_body = email_body.replace('\n', '<br>')
            html_part = MIMEText(f"""
            <html>
              <body>
                <p>{html_body}</p>
                <br>
                <p>Best regards,<br>
                {user.smtp_from_name or user.full_name}<br>
                {user.company_name or ''}</p>
              </body>
            </html>
            """, 'html')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Connect to SMTP server and send
            print(f"📧 Connecting to SMTP server {user.smtp_host}:{user.smtp_port}")
            
            with smtplib.SMTP(user.smtp_host, user.smtp_port) as server:
                server.starttls()  # Secure the connection
                print(f"   Logging in as {user.smtp_username}")
                server.login(user.smtp_username, user.smtp_password)
                print(f"   Sending email to {lead.contact_email}")
                server.send_message(msg)
                print(f"   ✅ Email sent successfully!")
            
            # Update lead status
            lead.status = 'contacted'
            lead.updated_at = datetime.utcnow()
            await lead.save()
            
            # Track email usage
            await EmailService.track_email_sent(user)
            
            return {
                "success": True,
                "message": f"Email sent successfully to {lead.contact_email}"
            }
            
        except smtplib.SMTPAuthenticationError:
            return {
                "success": False,
                "error": "SMTP authentication failed. Please check your username and password."
            }
        except smtplib.SMTPException as e:
            return {
                "success": False,
                "error": f"SMTP error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to send email: {str(e)}"
            }
    
    @staticmethod
    async def test_smtp_connection(user: User) -> dict:
        """Test SMTP connection with user's settings"""
        if not all([user.smtp_host, user.smtp_port, user.smtp_username, user.smtp_password]):
            return {
                "success": False,
                "error": "SMTP settings incomplete"
            }
        
        try:
            with smtplib.SMTP(user.smtp_host, user.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(user.smtp_username, user.smtp_password)
            
            return {
                "success": True,
                "message": "SMTP connection successful!"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Connection failed: {str(e)}"
            }
    
    @staticmethod
    async def track_email_sent(user: User):
        """Track email usage for analytics"""
        current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Find or create usage tracking for current month
        usage = await UsageTracking.find_one(
            UsageTracking.user.id == user.id,
            UsageTracking.month == current_month
        )
        
        if not usage:
            usage = UsageTracking(
                user=user,
                month=current_month,
                emails_sent=1
            )
        else:
            usage.emails_sent += 1
        
        await usage.save()
