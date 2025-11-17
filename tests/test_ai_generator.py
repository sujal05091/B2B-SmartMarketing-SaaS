"""
Unit tests for AIGenerator module
"""

import pytest
from src.core.ai_generator import AIGenerator


class TestAIGenerator:
    """Test cases for AIGenerator class."""
    
    @pytest.fixture
    def generator(self):
        """Create AIGenerator instance for testing."""
        return AIGenerator()
    
    def test_initialization(self, generator):
        """Test AIGenerator initialization."""
        assert generator is not None
        assert generator.backend in ["openai", "ollama"]
    
    def test_parse_email_response(self, generator):
        """Test email response parsing."""
        response = """
SUBJECT: Test Subject Line

BODY:
This is the email body.
Multiple paragraphs here.

Best regards,
Team
        """
        
        result = generator._parse_email_response(response)
        
        assert 'subject' in result
        assert 'body' in result
        assert "Test Subject Line" in result['subject']
    
    def test_generate_fallback_email(self, generator):
        """Test fallback email generation."""
        your_business = {
            'name': 'Test Company',
            'services': ['Service 1', 'Service 2']
        }
        lead = {'company_name': 'Lead Company'}
        matched_services = ['Service 1']
        
        email = generator._generate_fallback_email(your_business, lead, matched_services)
        
        assert 'Test Company' in email
        assert 'Lead Company' in email
    
    # TODO: Add more tests
    # - test_generate_outreach_email (mock AI responses)
    # - test_match_services_to_lead
    # - test_summarize_lead_business
