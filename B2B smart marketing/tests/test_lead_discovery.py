"""
Unit tests for LeadDiscovery module
"""

import pytest
from src.core.lead_discovery import LeadDiscovery


class TestLeadDiscovery:
    """Test cases for LeadDiscovery class."""
    
    @pytest.fixture
    def discovery(self):
        """Create LeadDiscovery instance for testing."""
        return LeadDiscovery()
    
    def test_initialization(self, discovery):
        """Test LeadDiscovery initialization."""
        assert discovery is not None
        assert discovery.config is not None
    
    def test_generate_search_queries(self, discovery):
        """Test search query generation."""
        services = ["Web Development", "SEO Services"]
        queries = discovery._generate_search_queries(services, "USA", "Technology")
        
        assert len(queries) > 0
        assert any("Web Development" in q for q in queries)
    
    def test_extract_domain(self, discovery):
        """Test domain extraction from URL."""
        url = "https://www.example.com/about"
        domain = discovery._extract_domain(url)
        
        assert domain == "example.com"
    
    # TODO: Add more tests
    # - test_discover_leads
    # - test_search_companies
    # - test_enrich_lead_contacts
