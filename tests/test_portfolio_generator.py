"""
Unit tests for PortfolioGenerator module
"""

import pytest
from src.core.portfolio_generator import PortfolioGenerator


class TestPortfolioGenerator:
    """Test cases for PortfolioGenerator class."""
    
    @pytest.fixture
    def generator(self):
        """Create PortfolioGenerator instance for testing."""
        return PortfolioGenerator()
    
    def test_initialization(self, generator):
        """Test PortfolioGenerator initialization."""
        assert generator is not None
        assert generator.output_dir.exists()
    
    def test_industry_colors(self, generator):
        """Test industry color schemes exist."""
        assert 'Technology' in generator.INDUSTRY_COLORS
        assert 'Marketing' in generator.INDUSTRY_COLORS
        assert 'default' in generator.INDUSTRY_COLORS
    
    # TODO: Add more tests
    # - test_generate_portfolio (with mock data)
    # - test_create_cover_page
    # - test_create_services_section
