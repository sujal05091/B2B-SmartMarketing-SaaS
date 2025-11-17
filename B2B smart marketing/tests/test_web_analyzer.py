"""
Unit tests for WebAnalyzer module
"""

import pytest
from src.core.web_analyzer import WebAnalyzer


class TestWebAnalyzer:
    """Test cases for WebAnalyzer class."""
    
    @pytest.fixture
    def analyzer(self):
        """Create WebAnalyzer instance for testing."""
        return WebAnalyzer()
    
    def test_initialization(self, analyzer):
        """Test WebAnalyzer initialization."""
        assert analyzer is not None
        assert analyzer.timeout == 10
    
    def test_extract_title(self, analyzer):
        """Test title extraction."""
        from bs4 import BeautifulSoup
        
        html = "<html><head><title>Test Company</title></head></html>"
        soup = BeautifulSoup(html, 'html.parser')
        
        title = analyzer._extract_title(soup)
        assert title == "Test Company"
    
    def test_extract_industry(self, analyzer):
        """Test industry detection."""
        from bs4 import BeautifulSoup
        
        html = "<html><body>We provide software development and cloud services</body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        
        industry = analyzer._extract_industry(soup)
        assert industry in ['Technology', 'General Business']
    
    # TODO: Add more tests
    # - test_analyze_website
    # - test_extract_services
    # - test_extract_email
    # - test_error_handling
