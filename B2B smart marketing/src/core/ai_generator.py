"""
AI Generator Module

Generates personalized B2B outreach emails and content using:
- OpenAI GPT models (GPT-4, GPT-3.5-turbo)
- Local LLaMA models via Ollama (optional)

Features:
- Personalized email generation
- Service matching
- Industry-specific messaging
- Tone customization
"""

import openai
import requests
from typing import Dict, List, Optional
from src.utils.logger import LoggerMixin
from src.utils.config import get_config


class AIGenerator(LoggerMixin):
    """
    AI-powered content generator for B2B marketing.
    
    Generates:
    - Personalized outreach emails
    - Service summaries
    - Company descriptions
    - Value propositions
    """
    
    def __init__(self):
        """Initialize AI Generator with API configuration."""
        self.setup_logging("AIGenerator")
        self.config = get_config()
        
        # Configure AI backend
        if self.config.USE_OLLAMA:
            self.backend = "ollama"
            self.log_info(f"Using Ollama with model: {self.config.OLLAMA_MODEL}")
        else:
            self.backend = "openai"
            openai.api_key = self.config.OPENAI_API_KEY
            self.log_info(f"Using OpenAI with model: {self.config.OPENAI_MODEL}")
    
    def generate_outreach_email(self, 
                                your_business: Dict,
                                lead: Dict,
                                matched_services: List[str],
                                tone: str = "professional") -> Dict:
        """
        Generate personalized B2B outreach email.
        
        Args:
            your_business: Your business information (name, description, services)
            lead: Lead information (company_name, website, description, industry)
            matched_services: Services relevant to this lead
            tone: Email tone (professional, friendly, casual)
        
        Returns:
            Dictionary with email content:
            {
                'subject': str,
                'body': str,
                'matched_services': List[str],
                'success': bool,
                'error': Optional[str]
            }
        """
        self.log_info(f"Generating outreach email for {lead.get('company_name', 'Unknown')}")
        
        try:
            # Build prompt
            prompt = self._build_email_prompt(your_business, lead, matched_services, tone)
            
            # Generate email
            if self.backend == "openai":
                response = self._generate_with_openai(prompt)
            else:
                response = self._generate_with_ollama(prompt)
            
            # Parse response
            email_content = self._parse_email_response(response)
            email_content['matched_services'] = matched_services
            email_content['success'] = True
            email_content['error'] = None
            
            self.log_info(f"Successfully generated email for {lead.get('company_name')}")
            return email_content
            
        except Exception as e:
            self.log_error(f"Error generating email: {e}", exc_info=True)
            return {
                'subject': f"Partnership Opportunity with {your_business.get('name', '')}",
                'body': self._generate_fallback_email(your_business, lead, matched_services),
                'matched_services': matched_services,
                'success': False,
                'error': str(e)
            }
    
    def _build_email_prompt(self, your_business: Dict, lead: Dict,
                           matched_services: List[str], tone: str) -> str:
        """
        Build prompt for email generation.
        
        Args:
            your_business: Your business info
            lead: Lead info
            matched_services: Matched services
            tone: Email tone
        
        Returns:
            Formatted prompt string
        """
        prompt = f"""
You are a B2B marketing expert writing a personalized outreach email.

YOUR COMPANY:
- Name: {your_business.get('name', 'Our Company')}
- Description: {your_business.get('description', 'We provide business services')}
- Services: {', '.join(your_business.get('services', [])[:5])}

LEAD COMPANY:
- Name: {lead.get('company_name', 'Unknown Company')}
- Website: {lead.get('website', 'N/A')}
- Description: {lead.get('description', 'No description available')}
- Industry: {lead.get('industry', 'General Business')}

MATCHED SERVICES:
{chr(10).join(f'- {service}' for service in matched_services)}

INSTRUCTIONS:
1. Write a personalized B2B outreach email with a {tone} tone
2. Keep it concise (150-200 words)
3. Highlight how the matched services can benefit their business
4. Focus on value proposition, not just features
5. Include a clear call-to-action
6. Make it engaging and professional
7. Use their company name and show you researched them

FORMAT:
Return ONLY the email in this exact format:

SUBJECT: [Write compelling subject line]

BODY:
[Write email body here]

Best regards,
{your_business.get('name', 'Our Team')}
"""
        return prompt.strip()
    
    def _generate_with_openai(self, prompt: str) -> str:
        """
        Generate content using OpenAI API.
        
        Args:
            prompt: Input prompt
        
        Returns:
            Generated text
        """
        try:
            response = openai.chat.completions.create(
                model=self.config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert B2B marketing copywriter specializing in personalized outreach."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.log_error(f"OpenAI API error: {e}")
            raise
    
    def _generate_with_ollama(self, prompt: str) -> str:
        """
        Generate content using Ollama (local LLaMA).
        
        Args:
            prompt: Input prompt
        
        Returns:
            Generated text
        """
        try:
            url = f"{self.config.OLLAMA_BASE_URL}/api/generate"
            payload = {
                "model": self.config.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            return data.get('response', '').strip()
            
        except Exception as e:
            self.log_error(f"Ollama API error: {e}")
            raise
    
    def _parse_email_response(self, response: str) -> Dict:
        """
        Parse AI response into subject and body.
        
        Args:
            response: AI-generated response
        
        Returns:
            Dictionary with subject and body
        """
        try:
            # Split by SUBJECT: and BODY:
            parts = response.split('BODY:', 1)
            
            if len(parts) == 2:
                subject_part = parts[0].replace('SUBJECT:', '').strip()
                body_part = parts[1].strip()
                
                return {
                    'subject': subject_part,
                    'body': body_part
                }
            else:
                # Fallback: use first line as subject
                lines = response.strip().split('\n')
                subject = lines[0] if lines else "Partnership Opportunity"
                body = '\n'.join(lines[1:]) if len(lines) > 1 else response
                
                return {
                    'subject': subject.replace('SUBJECT:', '').strip(),
                    'body': body.replace('BODY:', '').strip()
                }
                
        except Exception as e:
            self.log_error(f"Error parsing email response: {e}")
            return {
                'subject': "Partnership Opportunity",
                'body': response
            }
    
    def _generate_fallback_email(self, your_business: Dict, lead: Dict,
                                 matched_services: List[str]) -> str:
        """
        Generate fallback email if AI fails.
        
        Args:
            your_business: Your business info
            lead: Lead info
            matched_services: Matched services
        
        Returns:
            Fallback email body
        """
        company_name = lead.get('company_name', 'your company')
        your_name = your_business.get('name', 'our company')
        services_list = '\n'.join(f'• {service}' for service in matched_services[:3])
        
        email = f"""Dear {company_name} Team,

I hope this message finds you well. I'm reaching out from {your_name} because I believe we could provide significant value to {company_name}.

Based on your industry and business focus, we offer services that could benefit your operations:

{services_list}

We specialize in helping companies like yours achieve their business goals through our proven solutions.

I'd love to schedule a brief call to discuss how we can support {company_name}'s growth and success.

Are you available for a 15-minute conversation next week?

Best regards,
{your_name} Team"""
        
        return email
    
    def summarize_lead_business(self, lead: Dict, website_content: str) -> str:
        """
        Generate a summary of the lead's business.
        
        Args:
            lead: Lead information
            website_content: Content from lead's website
        
        Returns:
            Business summary
        """
        self.log_info(f"Summarizing business: {lead.get('company_name')}")
        
        try:
            prompt = f"""
Analyze the following information about a company and provide a concise 2-3 sentence summary of their business:

Company: {lead.get('company_name', 'Unknown')}
Website: {lead.get('website', 'N/A')}
Industry: {lead.get('industry', 'Unknown')}

Website Content:
{website_content[:1000]}

Provide a clear, professional summary of what this company does and their main offerings.
"""
            
            if self.backend == "openai":
                summary = self._generate_with_openai(prompt)
            else:
                summary = self._generate_with_ollama(prompt)
            
            self.log_info("Successfully generated business summary")
            return summary.strip()
            
        except Exception as e:
            self.log_error(f"Error summarizing business: {e}")
            return lead.get('description', 'Business description not available.')
    
    def match_services_to_lead(self, your_services: List[str],
                               lead: Dict,
                               website_content: str) -> List[str]:
        """
        Match your services to lead's needs using AI.
        
        Args:
            your_services: Your company's services
            lead: Lead information
            website_content: Content from lead's website
        
        Returns:
            List of matched services
        """
        self.log_info(f"Matching services for {lead.get('company_name')}")
        
        try:
            services_text = '\n'.join(f'{i+1}. {s}' for i, s in enumerate(your_services))
            
            prompt = f"""
Analyze which services would be most relevant and valuable for this company:

LEAD COMPANY:
Name: {lead.get('company_name')}
Industry: {lead.get('industry')}
Description: {lead.get('description', '')}

Website Content Summary:
{website_content[:500]}

AVAILABLE SERVICES:
{services_text}

TASK:
Select the 3-5 most relevant services that would benefit this company. Return ONLY the exact service names, one per line, without numbers or explanations.
"""
            
            if self.backend == "openai":
                response = self._generate_with_openai(prompt)
            else:
                response = self._generate_with_ollama(prompt)
            
            # Parse matched services
            matched = [line.strip() for line in response.split('\n') if line.strip()]
            matched = [s for s in matched if s in your_services][:5]
            
            # Fallback to first 3 services if no matches
            if not matched:
                matched = your_services[:3]
            
            self.log_info(f"Matched {len(matched)} services")
            return matched
            
        except Exception as e:
            self.log_error(f"Error matching services: {e}")
            return your_services[:3]  # Fallback
