"""Test email sending with PDF attachment"""
from src.utils.email_sender import EmailSender
import os

es = EmailSender()

# Find a PDF to attach
pdf_path = 'output/portfolios/Portfolio_General_Business_Services_-_Tipping_and_Company_20251026_155216.pdf'

if not os.path.exists(pdf_path):
    # Try another PDF
    import glob
    pdfs = glob.glob('output/portfolios/*.pdf')
    if pdfs:
        pdf_path = pdfs[-1]  # Use latest PDF
    else:
        pdf_path = None

print(f"\n📧 Sending test email to: martin.luther05091@gmail.com")
if pdf_path:
    print(f"📎 Attaching: {pdf_path}\n")
else:
    print("⚠️  No PDF found, sending without attachment\n")

result = es.send_email(
    recipient_email='martin.luther05091@gmail.com',
    subject='🎉 Test: B2B Marketing Assistant - Email with PDF Portfolio',
    body="""Hello!

This is a test email from your B2B Smart Marketing Assistant.

✅ If you received this with a PDF attachment, the auto-PDF feature is working perfectly!

The PDF portfolio is professionally branded and tailored for each potential client.

Best regards,
Your Smart Marketing Assistant
""",
    attachment_path=pdf_path
)

if result['success']:
    print("✅ Email sent successfully!")
    print("📧 Check your Gmail inbox: martin.luther05091@gmail.com")
    if pdf_path:
        print("📎 PDF portfolio should be attached!")
else:
    print(f"❌ Failed: {result['error']}")
