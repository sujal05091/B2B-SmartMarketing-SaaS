"""
Lead Discovery Module

Discovers potential B2B clients using legal open-web sources and free-tier APIs.

Supports:
- SerpAPI for Google search
- Bing Search API
- Google Custom Search API
- Hunter.io for email discovery
- Snov.io for contact enrichment
"""

import requests
import time
from typing import Dict, List, Optional
from urllib.parse import quote_plus
from src.utils.logger import LoggerMixin
from src.utils.config import get_config


class LeadDiscovery(LoggerMixin):
    """
    Discovers potential B2B clients using search APIs and web sources.
    
    Features:
    - Multi-API support (SerpAPI, Bing, Google)
    - Smart query generation
    - Result deduplication
    - Contact information enrichment
    - Rate limiting and retry logic
    """
    
    def __init__(self):
        """Initialize Lead Discovery with API configuration."""
        self.setup_logging("LeadDiscovery")
        self.config = get_config()
        self.discovered_leads = []
    
    def discover_leads(self, business_description: str, services: List[str],
                      max_leads: int = 10, region: Optional[str] = None,
                      industry: Optional[str] = None) -> List[Dict]:
        """
        Discover potential leads based on business services.
        
        Args:
            business_description: Description of your business
            services: List of services offered
            max_leads: Maximum number of leads to discover
            region: Geographic region to focus on (optional)
            industry: Industry to target (optional)
        
        Returns:
            List of lead dictionaries with company information
        """
        self.log_info(f"Starting lead discovery (max: {max_leads})")
        
        # Generate search queries
        queries = self._generate_search_queries(services, region, industry)
        
        leads = []
        seen_domains = set()
        
        for query in queries:
            if len(leads) >= max_leads:
                break
            
            # Search using available APIs
            search_results = self._search_companies(query)
            
            # Process results
            for result in search_results:
                if len(leads) >= max_leads:
                    break
                
                # Extract domain for deduplication
                domain = self._extract_domain(result.get('url', ''))
                if domain in seen_domains:
                    continue
                
                # Create lead entry
                lead = {
                    'company_name': result.get('title', 'Unknown Company'),
                    'website': result.get('url', ''),
                    'description': result.get('snippet', ''),
                    'source_query': query,
                    'industry': industry or 'Unknown',
                    'region': region or 'Global',
                    'discovered_at': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                
                leads.append(lead)
                seen_domains.add(domain)
                self.log_debug(f"Found lead: {lead['company_name']}")
            
            # Rate limiting between queries
            time.sleep(self.config.API_RATE_LIMIT_DELAY)
        
        self.log_info(f"Discovered {len(leads)} unique leads")
        self.discovered_leads = leads
        return leads
    
    def _generate_search_queries(self, services: List[str], 
                                 region: Optional[str],
                                 industry: Optional[str]) -> List[str]:
        """
        Generate search queries to find REAL companies (not directories).
        
        Args:
            services: List of services
            region: Geographic region
            industry: Industry type
        
        Returns:
            List of search query strings optimized for real companies
        """
        queries = []
        
        # Target actual company websites with contact info
        # Exclude directories, lists, rankings, and top-10 articles
        exclude_terms = "-list -directory -top -ranking -forbes -best -review"
        
        # Base query templates targeting real companies
        templates = [
            '"{service}" company contact email',
            '"{service}" business "contact us"',
            'site:linkedin.com/company {service}',
            '{service} company website email',
            '"{service}" "about us" "contact"'
        ]
        
        # Add region if specified
        region_suffix = f" {region}" if region else " USA"
        
        # Add industry if specified
        industry_prefix = f"{industry} " if industry else ""
        
        # Generate queries for each service (limit to top 3 services)
        for service in services[:3]:
            for template in templates[:2]:  # Limit templates per service
                query = template.format(service=service)
                # Add location and exclude directories
                query = f"{industry_prefix}{query}{region_suffix} {exclude_terms}"
                queries.append(query)
        
        # Add specific company-finding queries
        if industry:
            queries.extend([
                f'{industry} company "contact us" {region_suffix} {exclude_terms}',
                f'site:linkedin.com/company {industry}{region_suffix}',
                f'{industry} business email address {region_suffix} {exclude_terms}'
            ])
        else:
            queries.extend([
                f'small business "contact us" {region_suffix} {exclude_terms}',
                f'company website contact {region_suffix} {exclude_terms}'
            ])
        
        self.log_debug(f"Generated {len(queries)} search queries (optimized for real companies)")
        return queries[:8]  # Limit total queries
    
    def _search_companies(self, query: str) -> List[Dict]:
        """
        Search for companies using available APIs.
        
        Args:
            query: Search query string
        
        Returns:
            List of search results
        """
        # Try SerpAPI first
        if self.config.SERPAPI_KEY:
            results = self._search_with_serpapi(query)
            if results:
                return results
        
        # Try Bing Search
        if self.config.BING_SEARCH_API_KEY:
            results = self._search_with_bing(query)
            if results:
                return results
        
        # Try Google Custom Search
        if self.config.GOOGLE_CUSTOM_SEARCH_API_KEY:
            results = self._search_with_google(query)
            if results:
                return results
        
        self.log_warning(f"No search results for query: {query}")
        return []
    
    def _search_with_serpapi(self, query: str) -> List[Dict]:
        """
        Search using SerpAPI.
        
        Args:
            query: Search query
        
        Returns:
            List of search results
        """
        try:
            url = "https://serpapi.com/search"
            params = {
                'q': query,
                'api_key': self.config.SERPAPI_KEY,
                'num': 10,
                'engine': 'google'
            }
            
            self.log_debug(f"Searching with SerpAPI: {query}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get('organic_results', [])[:10]:
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('link', ''),
                    'snippet': item.get('snippet', '')
                })
            
            self.log_debug(f"SerpAPI returned {len(results)} results")
            return results
            
        except Exception as e:
            self.log_error(f"SerpAPI error: {e}")
            return []
    
    def _search_with_bing(self, query: str) -> List[Dict]:
        """
        Search using Bing Search API.
        
        Args:
            query: Search query
        
        Returns:
            List of search results
        """
        try:
            url = "https://api.bing.microsoft.com/v7.0/search"
            headers = {'Ocp-Apim-Subscription-Key': self.config.BING_SEARCH_API_KEY}
            params = {'q': query, 'count': 10}
            
            self.log_debug(f"Searching with Bing: {query}")
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get('webPages', {}).get('value', [])[:10]:
                results.append({
                    'title': item.get('name', ''),
                    'url': item.get('url', ''),
                    'snippet': item.get('snippet', '')
                })
            
            self.log_debug(f"Bing returned {len(results)} results")
            return results
            
        except Exception as e:
            self.log_error(f"Bing API error: {e}")
            return []
    
    def _search_with_google(self, query: str) -> List[Dict]:
        """
        Search using Google Custom Search API.
        
        Args:
            query: Search query
        
        Returns:
            List of search results
        """
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.config.GOOGLE_CUSTOM_SEARCH_API_KEY,
                'cx': self.config.GOOGLE_CUSTOM_SEARCH_ENGINE_ID,
                'q': query,
                'num': 10
            }
            
            self.log_debug(f"Searching with Google Custom Search: {query}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get('items', [])[:10]:
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('link', ''),
                    'snippet': item.get('snippet', '')
                })
            
            self.log_debug(f"Google returned {len(results)} results")
            return results
            
        except Exception as e:
            self.log_error(f"Google Custom Search error: {e}")
            return []
    
    def _extract_domain(self, url: str) -> str:
        """
        Extract domain from URL for deduplication.
        
        Args:
            url: Full URL
        
        Returns:
            Domain name
        """
        from urllib.parse import urlparse
        try:
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path
            # Remove www. prefix
            domain = domain.replace('www.', '')
            return domain.lower()
        except:
            return url.lower()
    
    def enrich_lead_contacts(self, lead: Dict) -> Dict:
        """
        Enrich lead with contact information using Hunter.io or Snov.io.
        
        Args:
            lead: Lead dictionary
        
        Returns:
            Enriched lead dictionary with contact info
        """
        domain = self._extract_domain(lead.get('website', ''))
        
        # Try Hunter.io
        if self.config.HUNTER_IO_API_KEY:
            contacts = self._find_emails_hunter(domain)
            if contacts:
                lead['contacts'] = contacts
                return lead
        
        # Try Snov.io
        if self.config.SNOV_IO_API_KEY:
            contacts = self._find_emails_snov(domain)
            if contacts:
                lead['contacts'] = contacts
                return lead
        
        lead['contacts'] = []
        return lead
    
    def _find_emails_hunter(self, domain: str) -> List[Dict]:
        """
        Find email addresses using Hunter.io.
        
        Args:
            domain: Company domain
        
        Returns:
            List of contact dictionaries
        """
        try:
            url = "https://api.hunter.io/v2/domain-search"
            params = {
                'domain': domain,
                'api_key': self.config.HUNTER_IO_API_KEY,
                'limit': 5
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            contacts = []
            
            for email_data in data.get('data', {}).get('emails', [])[:5]:
                contacts.append({
                    'email': email_data.get('value', ''),
                    'first_name': email_data.get('first_name', ''),
                    'last_name': email_data.get('last_name', ''),
                    'position': email_data.get('position', ''),
                    'confidence': email_data.get('confidence', 0)
                })
            
            return contacts
            
        except Exception as e:
            self.log_error(f"Hunter.io error: {e}")
            return []
    
    def _find_emails_snov(self, domain: str) -> List[Dict]:
        """
        Find email addresses using Snov.io.
        
        Args:
            domain: Company domain
        
        Returns:
            List of contact dictionaries
        """
        try:
            # TODO: Implement Snov.io API integration
            # Placeholder for now
            self.log_debug("Snov.io integration placeholder")
            return []
            
        except Exception as e:
            self.log_error(f"Snov.io error: {e}")
            return []
