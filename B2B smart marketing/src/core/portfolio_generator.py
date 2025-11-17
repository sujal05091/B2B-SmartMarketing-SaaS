"""
Portfolio Generator Module

Creates customized PDF portfolios using ReportLab.

Features:
- Dynamic styling based on industry
- Company branding and logo
- Service highlights
- Case studies/testimonials
- Contact information
- Professional layouts
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from src.utils.logger import LoggerMixin
from src.utils.config import get_config


class PortfolioGenerator(LoggerMixin):
    """
    Generates customized PDF portfolios for B2B outreach.
    
    Features:
    - Industry-specific color schemes
    - Dynamic layouts
    - Service showcases
    - Professional formatting
    """
    
    # Industry color schemes (Primary, Secondary, Accent)
    INDUSTRY_COLORS = {
        'Technology': (colors.HexColor('#0066CC'), colors.HexColor('#00A8E8'), colors.HexColor('#F0F4F8')),
        'Marketing': (colors.HexColor('#FF6B35'), colors.HexColor('#004E89'), colors.HexColor('#FFF5E1')),
        'Finance': (colors.HexColor('#1A5490'), colors.HexColor('#2E8BC0'), colors.HexColor('#E8F4F8')),
        'Healthcare': (colors.HexColor('#00A8A8'), colors.HexColor('#4ECDC4'), colors.HexColor('#F0F9F9')),
        'Education': (colors.HexColor('#5B4B8A'), colors.HexColor('#8E7CC3'), colors.HexColor('#F5F3FF')),
        'Consulting': (colors.HexColor('#2C3E50'), colors.HexColor('#34495E'), colors.HexColor('#ECF0F1')),
        'Manufacturing': (colors.HexColor('#E67E22'), colors.HexColor('#D68910'), colors.HexColor('#FEF5E7')),
        'Real Estate': (colors.HexColor('#27AE60'), colors.HexColor('#52BE80'), colors.HexColor('#E8F8F5')),
        'Legal': (colors.HexColor('#8B4513'), colors.HexColor('#A0522D'), colors.HexColor('#FFF8DC')),
        'default': (colors.HexColor('#333333'), colors.HexColor('#666666'), colors.HexColor('#F5F5F5'))
    }
    
    def __init__(self):
        """Initialize Portfolio Generator."""
        self.setup_logging("PortfolioGenerator")
        self.config = get_config()
        self.output_dir = self.config.PORTFOLIO_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_portfolio(self,
                          your_business: Dict,
                          lead: Dict,
                          matched_services: List[str],
                          email_content: Dict) -> Dict:
        """
        Generate a customized PDF portfolio for a lead.
        
        Args:
            your_business: Your business information
            lead: Lead company information
            matched_services: Services matched to this lead
            email_content: Generated email content
        
        Returns:
            Dictionary with portfolio info:
            {
                'file_path': str,
                'file_name': str,
                'success': bool,
                'error': Optional[str]
            }
        """
        self.log_info(f"Generating portfolio for {lead.get('company_name', 'Unknown')}")
        
        try:
            # Generate file name
            company_name = lead.get('company_name', 'Unknown').replace(' ', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_name = f"Portfolio_{company_name}_{timestamp}.pdf"
            file_path = self.output_dir / file_name
            
            # Get industry colors
            industry = lead.get('industry', 'default')
            colors_scheme = self.INDUSTRY_COLORS.get(industry, self.INDUSTRY_COLORS['default'])
            
            # Create PDF
            doc = SimpleDocTemplate(
                str(file_path),
                pagesize=letter,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch
            )
            
            # Build content
            story = []
            story.extend(self._create_cover_page(your_business, lead, colors_scheme))
            story.append(PageBreak())
            story.extend(self._create_introduction(your_business, lead, colors_scheme))
            story.append(Spacer(1, 0.3*inch))
            story.extend(self._create_services_section(matched_services, your_business, colors_scheme))
            story.append(Spacer(1, 0.3*inch))
            story.extend(self._create_value_proposition(your_business, lead, colors_scheme))
            story.append(Spacer(1, 0.3*inch))
            story.extend(self._create_contact_section(your_business, colors_scheme))
            
            # Build PDF
            doc.build(story)
            
            self.log_info(f"Successfully created portfolio: {file_path}")
            return {
                'file_path': str(file_path),
                'file_name': file_name,
                'success': True,
                'error': None
            }
            
        except Exception as e:
            self.log_error(f"Error generating portfolio: {e}", exc_info=True)
            return {
                'file_path': '',
                'file_name': '',
                'success': False,
                'error': str(e)
            }
    
    def _create_cover_page(self, your_business: Dict, lead: Dict, colors_scheme: tuple) -> List:
        """Create cover page elements."""
        elements = []
        styles = getSampleStyleSheet()
        
        primary_color, secondary_color, bg_color = colors_scheme
        
        # Add spacing
        elements.append(Spacer(1, 1.5*inch))
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=32,
            textColor=primary_color,
            alignment=TA_CENTER,
            spaceAfter=30,
            fontName='Helvetica-Bold'
        )
        
        elements.append(Paragraph(
            f"{your_business.get('name', 'Our Company')}",
            title_style
        ))
        
        # Subtitle
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=18,
            textColor=secondary_color,
            alignment=TA_CENTER,
            spaceAfter=40
        )
        
        elements.append(Paragraph(
            "Business Partnership Proposal",
            subtitle_style
        ))
        
        elements.append(Spacer(1, 0.5*inch))
        
        # Prepared for
        prepared_style = ParagraphStyle(
            'Prepared',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.grey,
            alignment=TA_CENTER,
            spaceAfter=10
        )
        
        elements.append(Paragraph(
            f"Prepared for:<br/><b>{lead.get('company_name', 'Your Company')}</b>",
            prepared_style
        ))
        
        elements.append(Spacer(1, 1*inch))
        
        # Date
        date_style = ParagraphStyle(
            'Date',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        
        elements.append(Paragraph(
            datetime.now().strftime('%B %d, %Y'),
            date_style
        ))
        
        return elements
    
    def _create_introduction(self, your_business: Dict, lead: Dict, colors_scheme: tuple) -> List:
        """Create introduction section."""
        elements = []
        styles = getSampleStyleSheet()
        
        primary_color, secondary_color, bg_color = colors_scheme
        
        # Section title
        heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=20,
            textColor=primary_color,
            spaceAfter=15,
            fontName='Helvetica-Bold',
            borderPadding=(0, 0, 5, 0),
            borderColor=primary_color,
            borderWidth=2,
            borderRadius=0
        )
        
        elements.append(Paragraph("About Us", heading_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Company description
        body_style = ParagraphStyle(
            'BodyText',
            parent=styles['Normal'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            leading=16
        )
        
        description = your_business.get('description', 'We provide professional business services.')
        elements.append(Paragraph(description, body_style))
        
        # Personalized message
        elements.append(Spacer(1, 0.2*inch))
        personalized = f"""
        We've researched <b>{lead.get('company_name', 'your company')}</b> and believe our services 
        align perfectly with your business needs in the {lead.get('industry', 'industry')} sector. 
        This portfolio outlines how we can help you achieve your business objectives.
        """
        elements.append(Paragraph(personalized, body_style))
        
        return elements
    
    def _create_services_section(self, services: List[str], your_business: Dict, colors_scheme: tuple) -> List:
        """Create services showcase section."""
        elements = []
        styles = getSampleStyleSheet()
        
        primary_color, secondary_color, bg_color = colors_scheme
        
        # Section title
        heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=20,
            textColor=primary_color,
            spaceAfter=15,
            fontName='Helvetica-Bold'
        )
        
        elements.append(Paragraph("Our Recommended Services for You", heading_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Services table
        service_data = []
        
        for i, service in enumerate(services, 1):
            service_data.append([
                Paragraph(f"<b>{i}.</b>", styles['Normal']),
                Paragraph(f"<b>{service}</b><br/>Tailored solution to enhance your business operations.", styles['Normal'])
            ])
        
        service_table = Table(service_data, colWidths=[0.5*inch, 5.5*inch])
        service_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TEXTCOLOR', (0, 0), (0, -1), primary_color),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (1, 0), (1, -1), bg_color),
            ('BOX', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.lightgrey),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        elements.append(service_table)
        
        return elements
    
    def _create_value_proposition(self, your_business: Dict, lead: Dict, colors_scheme: tuple) -> List:
        """Create value proposition section."""
        elements = []
        styles = getSampleStyleSheet()
        
        primary_color, secondary_color, bg_color = colors_scheme
        
        # Section title
        heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=20,
            textColor=primary_color,
            spaceAfter=15,
            fontName='Helvetica-Bold'
        )
        
        elements.append(Paragraph("Why Choose Us", heading_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Value points
        value_points = [
            ("Expertise", "Years of proven experience in delivering results"),
            ("Customization", "Tailored solutions designed for your specific needs"),
            ("Support", "Dedicated support team available throughout your journey"),
            ("Results", "Track record of successful client partnerships")
        ]
        
        body_style = ParagraphStyle(
            'BodyText',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=10,
            leftIndent=20,
            bulletIndent=10
        )
        
        for title, description in value_points:
            elements.append(Paragraph(
                f"<b><font color='{primary_color}'>✓ {title}:</font></b> {description}",
                body_style
            ))
        
        return elements
    
    def _create_contact_section(self, your_business: Dict, colors_scheme: tuple) -> List:
        """Create contact information section."""
        elements = []
        styles = getSampleStyleSheet()
        
        primary_color, secondary_color, bg_color = colors_scheme
        
        elements.append(Spacer(1, 0.5*inch))
        
        # Section title
        heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=18,
            textColor=primary_color,
            spaceAfter=15,
            fontName='Helvetica-Bold'
        )
        
        elements.append(Paragraph("Let's Connect", heading_style))
        
        # Contact info
        contact_style = ParagraphStyle(
            'Contact',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=8
        )
        
        contact_info = f"""
        <b>{your_business.get('name', 'Our Company')}</b><br/>
        Website: {your_business.get('url', 'www.example.com')}<br/>
        Email: {your_business.get('contact_email', 'contact@example.com')}<br/>
        """
        
        elements.append(Paragraph(contact_info, contact_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Call to action
        cta_style = ParagraphStyle(
            'CTA',
            parent=styles['Normal'],
            fontSize=12,
            textColor=secondary_color,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        )
        
        elements.append(Paragraph(
            "We look forward to partnering with you!",
            cta_style
        ))
        
        return elements
