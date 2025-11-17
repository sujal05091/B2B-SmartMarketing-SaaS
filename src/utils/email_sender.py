"""
Email Sender Module (Bonus Feature)

Automatically sends outreach emails using SMTP.

Features:
- SMTP integration
- Email validation
- Batch sending with rate limiting
- Delivery tracking
- Error handling
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import Dict, List, Optional
import time
import os
from pathlib import Path
from src.utils.logger import LoggerMixin
from src.utils.config import get_config


class EmailSender(LoggerMixin):
    """
    Handles automated email sending for outreach campaigns.
    
    Features:
    - SMTP authentication
    - HTML email support
    - Batch sending
    - Rate limiting
    - Error handling and retry
    """
    
    def __init__(self):
        """Initialize Email Sender with SMTP configuration."""
        self.setup_logging("EmailSender")
        self.config = get_config()
        
        # SMTP configuration
        self.smtp_host = self.config.SMTP_HOST
        self.smtp_port = self.config.SMTP_PORT
        self.smtp_username = self.config.SMTP_USERNAME
        self.smtp_password = self.config.SMTP_PASSWORD
        self.sender_email = self.config.SENDER_EMAIL
        self.sender_name = self.config.SENDER_NAME
        
        self.log_info("Email Sender initialized")
    
    def send_email(self, recipient_email: str, subject: str, 
                   body: str, html_body: Optional[str] = None,
                   attachment_path: Optional[str] = None) -> Dict:
        """
        Send a single email with optional PDF attachment.
        
        Args:
            recipient_email: Recipient's email address
            subject: Email subject
            body: Plain text email body
            html_body: HTML email body (optional)
            attachment_path: Path to PDF file to attach (optional)
        
        Returns:
            Dictionary with sending result
        """
        self.log_info(f"Sending email to: {recipient_email}")
        
        try:
            # Validate configuration
            if not all([self.smtp_username, self.smtp_password, self.sender_email]):
                raise ValueError("SMTP configuration incomplete")
            
            # Create message
            message = MIMEMultipart('mixed')
            message['Subject'] = subject
            message['From'] = f"{self.sender_name} <{self.sender_email}>"
            message['To'] = recipient_email
            
            # Create alternative part for text/html
            msg_alternative = MIMEMultipart('alternative')
            message.attach(msg_alternative)
            
            # Attach plain text
            text_part = MIMEText(body, 'plain')
            msg_alternative.attach(text_part)
            
            # Attach HTML if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg_alternative.attach(html_part)
            
            # Attach PDF if provided
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, 'rb') as f:
                    pdf_attachment = MIMEApplication(f.read(), _subtype='pdf')
                    pdf_filename = Path(attachment_path).name
                    pdf_attachment.add_header(
                        'Content-Disposition',
                        'attachment',
                        filename=pdf_filename
                    )
                    message.attach(pdf_attachment)
                    self.log_info(f"Attached PDF: {pdf_filename}")
            
            # Connect to SMTP server and send
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(message)
            
            self.log_info(f"Email sent successfully to {recipient_email}")
            return {
                'success': True,
                'recipient': recipient_email,
                'error': None
            }
            
        except Exception as e:
            self.log_error(f"Failed to send email to {recipient_email}: {e}")
            return {
                'success': False,
                'recipient': recipient_email,
                'error': str(e)
            }
    
    def send_batch(self, emails: List[Dict], delay: int = 5) -> Dict:
        """
        Send multiple emails with rate limiting.
        
        Args:
            emails: List of email dictionaries with 'to', 'subject', 'body'
            delay: Delay between emails in seconds
        
        Returns:
            Dictionary with batch sending results
        """
        self.log_info(f"Sending batch of {len(emails)} emails")
        
        results = {
            'total': len(emails),
            'sent': 0,
            'failed': 0,
            'errors': []
        }
        
        for i, email_data in enumerate(emails, 1):
            self.log_debug(f"Sending email {i}/{len(emails)}")
            
            result = self.send_email(
                recipient_email=email_data.get('to', ''),
                subject=email_data.get('subject', ''),
                body=email_data.get('body', ''),
                html_body=email_data.get('html_body')
            )
            
            if result['success']:
                results['sent'] += 1
            else:
                results['failed'] += 1
                results['errors'].append({
                    'recipient': result['recipient'],
                    'error': result['error']
                })
            
            # Rate limiting
            if i < len(emails):
                time.sleep(delay)
        
        self.log_info(f"Batch complete: {results['sent']} sent, {results['failed']} failed")
        return results
    
    def convert_to_html(self, plain_text: str) -> str:
        """
        Convert plain text email to HTML format.
        
        Args:
            plain_text: Plain text email body
        
        Returns:
            HTML formatted email
        """
        # Simple conversion: paragraphs and line breaks
        paragraphs = plain_text.split('\n\n')
        html_paragraphs = [f"<p>{p.replace(chr(10), '<br>')}</p>" for p in paragraphs if p.strip()]
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        p {{
            margin-bottom: 15px;
        }}
    </style>
</head>
<body>
    {''.join(html_paragraphs)}
</body>
</html>
        """
        
        return html.strip()
    
    def validate_email(self, email: str) -> bool:
        """
        Validate email address format.
        
        Args:
            email: Email address to validate
        
        Returns:
            True if valid, False otherwise
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))


# Example usage
if __name__ == "__main__":
    # This is a standalone test/demo
    sender = EmailSender()
    
    # Test single email
    result = sender.send_email(
        recipient_email="test@example.com",
        subject="Test Email",
        body="This is a test email from Smart Marketing Assistant."
    )
    
    print(f"Email sent: {result['success']}")
