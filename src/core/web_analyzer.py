"""
Web Analyzer Module

Analyzes business websites to extract key information including:
- Company description and mission
- Services offered
- Industry/sector
- Contact information
- Key value propositions
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse
import time
from src.utils.logger import LoggerMixin


class WebAnalyzer(LoggerMixin):
    """
    Analyzes business websites to extract services and key information.
    
    Uses BeautifulSoup for HTML parsing and extracts:
    - Services and offerings
    - Company description
    - Industry type
    - Contact information
    """
    
    def __init__(self, timeout: int = 10):
        """
        Initialize Web Analyzer.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.setup_logging("WebAnalyzer")
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def analyze_website(self, url: str) -> Dict:
        """
        Analyze a business website and extract key information.
        
        Args:
            url: Website URL to analyze
        
        Returns:
            Dictionary containing extracted information:
            {
                'url': str,
                'title': str,
                'description': str,
                'services': List[str],
                'industry': str,
                'keywords': List[str],
                'contact_email': Optional[str],
                'contact_phone': Optional[str],
                'success': bool,
                'error': Optional[str]
            }
        """
        self.log_info(f"Analyzing website: {url}")
        
        try:
            # Fetch website content
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract information
            result = {
                'url': url,
                'title': self._extract_title(soup),
                'description': self._extract_description(soup),
                'services': self._extract_services(soup),
                'industry': self._extract_industry(soup),
                'keywords': self._extract_keywords(soup),
                'contact_email': self._extract_email(soup),
                'contact_phone': self._extract_phone(soup),
                'main_content': self._extract_main_content(soup),
                'success': True,
                'error': None
            }
            
            self.log_info(f"Successfully analyzed {url}: found {len(result['services'])} services")
            return result
            
        except requests.RequestException as e:
            self.log_error(f"Error fetching {url}: {e}")
            return {
                'url': url,
                'title': '',
                'description': '',
                'services': [],
                'industry': 'Unknown',
                'keywords': [],
                'contact_email': None,
                'contact_phone': None,
                'main_content': '',
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            self.log_error(f"Unexpected error analyzing {url}: {e}", exc_info=True)
            return {
                'url': url,
                'success': False,
                'error': f"Unexpected error: {str(e)}"
            }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        # Fallback to h1
        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.get_text().strip()
        
        return "Unknown"
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description or about text."""
        # Try meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()
        
        # Try og:description
        og_desc = soup.find('meta', property='og:description')
        if og_desc and og_desc.get('content'):
            return og_desc['content'].strip()
        
        # Fallback: extract from first paragraph
        paragraphs = soup.find_all('p')
        for p in paragraphs[:3]:
            text = p.get_text().strip()
            if len(text) > 50:
                return text[:300] + "..." if len(text) > 300 else text
        
        return "No description available"
    
    def _extract_services(self, soup: BeautifulSoup) -> List[str]:
        """
        Extract services from website.
        
        Looks for:
        - Service sections
        - Lists of offerings
        - Cards/divs with service descriptions
        """
        services = []
        
        # Keywords that indicate services
        service_keywords = ['service', 'solution', 'offering', 'product', 'expertise', 'specialization']
        
        # Look for sections with service keywords
        for keyword in service_keywords:
            sections = soup.find_all(['div', 'section', 'ul'], 
                                    class_=lambda x: x and keyword in x.lower() if x else False)
            for section in sections:
                # Extract list items
                items = section.find_all('li')
                for item in items:
                    service_text = item.get_text().strip()
                    if service_text and len(service_text) < 100:
                        services.append(service_text)
                
                # Extract headings
                headings = section.find_all(['h2', 'h3', 'h4'])
                for heading in headings:
                    service_text = heading.get_text().strip()
                    if service_text and len(service_text) < 100:
                        services.append(service_text)
        
        # Remove duplicates and limit
        services = list(dict.fromkeys(services))[:15]
        
        return services if services else ["General Business Services"]
    
    def _extract_industry(self, soup: BeautifulSoup) -> str:
        """
        Determine industry/sector from website content.
        
        Uses keyword matching and context analysis.
        """
        text_content = soup.get_text().lower()
        
        # Industry keywords mapping
        industries = {
            'Technology': ['software', 'tech', 'digital', 'cloud', 'saas', 'ai', 'development'],
            'Marketing': ['marketing', 'advertising', 'seo', 'branding', 'social media'],
            'Finance': ['finance', 'accounting', 'investment', 'banking', 'financial'],
            'Healthcare': ['health', 'medical', 'healthcare', 'clinical', 'hospital'],
            'Education': ['education', 'training', 'learning', 'course', 'academic'],
            'Consulting': ['consulting', 'advisory', 'strategy', 'management consulting'],
            'Manufacturing': ['manufacturing', 'production', 'factory', 'industrial'],
            'Real Estate': ['real estate', 'property', 'commercial', 'residential'],
            'Legal': ['legal', 'law', 'attorney', 'lawyer', 'litigation'],
            'E-commerce': ['ecommerce', 'e-commerce', 'online store', 'retail']
        }
        
        # Count matches
        matches = {}
        for industry, keywords in industries.items():
            count = sum(text_content.count(keyword) for keyword in keywords)
            if count > 0:
                matches[industry] = count
        
        # Return industry with most matches
        if matches:
            return max(matches, key=matches.get)
        
        return 'General Business'
    
    def _extract_keywords(self, soup: BeautifulSoup) -> List[str]:
        """Extract meta keywords."""
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords and meta_keywords.get('content'):
            keywords = meta_keywords['content'].split(',')
            return [kw.strip() for kw in keywords[:10]]
        return []
    
    def _extract_email(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract contact email if available."""
        # Look for email in contact links
        email_links = soup.find_all('a', href=lambda x: x and 'mailto:' in x)
        if email_links:
            email = email_links[0]['href'].replace('mailto:', '')
            return email.strip()
        
        # TODO: Could add regex pattern matching for emails in text
        return None
    
    def _extract_phone(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract contact phone if available."""
        # Look for tel: links
        phone_links = soup.find_all('a', href=lambda x: x and 'tel:' in x)
        if phone_links:
            phone = phone_links[0]['href'].replace('tel:', '')
            return phone.strip()
        
        return None
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """
        Extract main content text from website.
        
        Returns:
            Cleaned main content (limited to 1000 chars)
        """
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Limit length
        return text[:1000] + "..." if len(text) > 1000 else text
    
    def analyze_multiple_pages(self, base_url: str, pages: List[str]) -> Dict:
        """
        Analyze multiple pages of a website.
        
        Args:
            base_url: Base website URL
            pages: List of page paths to analyze (e.g., ['/about', '/services'])
        
        Returns:
            Combined analysis from all pages
        """
        self.log_info(f"Analyzing multiple pages for {base_url}")
        
        combined_result = {
            'url': base_url,
            'services': [],
            'description': '',
            'main_content': ''
        }
        
        for page in pages:
            url = urljoin(base_url, page)
            result = self.analyze_website(url)
            
            if result.get('success'):
                combined_result['services'].extend(result.get('services', []))
                if not combined_result['description'] and result.get('description'):
                    combined_result['description'] = result['description']
                combined_result['main_content'] += ' ' + result.get('main_content', '')
            
            time.sleep(1)  # Rate limiting
        
        # Remove duplicate services
        combined_result['services'] = list(dict.fromkeys(combined_result['services']))
        
        return combined_result
