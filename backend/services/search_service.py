import requests
import json
from typing import List, Dict, Optional
from models.user import User

class SearchService:
    """Service for searching businesses using SerpAPI"""
    
    @staticmethod
    async def search_businesses(
        user: User,
        industry: str,
        location: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Search for businesses using SerpAPI Google Search
        
        Args:
            user: User with SerpAPI key
            industry: Industry/business type to search
            location: Location to search in
            limit: Maximum number of results
            
        Returns:
            List of business data dictionaries
        """
        if not user.serpapi_key:
            return {"error": "SerpAPI key not configured"}
        
        try:
            # Build search query
            query = f"{industry} in {location}"
            
            # SerpAPI request
            params = {
                "engine": "google",
                "q": query,
                "api_key": user.serpapi_key,
                "num": limit,
            }
            
            print(f"🔍 Searching Google: {query}")
            response = requests.get("https://serpapi.com/search", params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            businesses = []
            
            # Extract organic results
            organic_results = data.get("organic_results", [])
            for result in organic_results[:limit]:
                business = {
                    "company_name": result.get("title", ""),
                    "website": result.get("link", ""),
                    "description": result.get("snippet", ""),
                    "industry": industry,
                }
                businesses.append(business)
                print(f"   ✓ Found: {business['company_name']}")
            
            # Also check local results (Google Maps)
            local_results = data.get("local_results", {}).get("places", [])
            for place in local_results[:limit - len(businesses)]:
                business = {
                    "company_name": place.get("title", ""),
                    "website": place.get("website", place.get("link", "")),
                    "description": place.get("description", place.get("type", "")),
                    "industry": industry,
                    "address": place.get("address", ""),
                    "phone": place.get("phone", ""),
                    "rating": place.get("rating"),
                }
                businesses.append(business)
                print(f"   ✓ Found (Local): {business['company_name']}")
            
            print(f"📊 Total businesses found: {len(businesses)}")
            return businesses
            
        except requests.RequestException as e:
            print(f"❌ SerpAPI Error: {str(e)}")
            return {"error": f"Search failed: {str(e)}"}
        except Exception as e:
            print(f"❌ Unexpected Error: {str(e)}")
            return {"error": f"Search error: {str(e)}"}
    
    @staticmethod
    async def find_email(
        user: User,
        domain: str,
        company_name: str
    ) -> Optional[str]:
        """
        Find email address for a domain using Hunter.io
        
        Args:
            user: User with Hunter.io API key
            domain: Company domain
            company_name: Company name
            
        Returns:
            Email address or None
        """
        if not user.hunter_api_key:
            print(f"   ⚠️ Hunter.io not configured, skipping email search")
            return None
        
        try:
            # Extract domain from URL if full URL provided
            if domain.startswith("http"):
                from urllib.parse import urlparse
                parsed = urlparse(domain)
                domain = parsed.netloc or parsed.path
            
            # Remove www. prefix
            domain = domain.replace("www.", "")
            
            print(f"   🔍 Finding email for {domain}")
            
            # Hunter.io Domain Search API
            url = "https://api.hunter.io/v2/domain-search"
            params = {
                "domain": domain,
                "api_key": user.hunter_api_key,
                "limit": 1,
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # Get the first email found
            emails = data.get("data", {}).get("emails", [])
            if emails:
                email = emails[0].get("value")
                print(f"   ✅ Found email: {email}")
                return email
            else:
                print(f"   ⚠️ No email found for {domain}")
                return None
                
        except requests.RequestException as e:
            print(f"   ❌ Hunter.io Error: {str(e)}")
            return None
        except Exception as e:
            print(f"   ❌ Email search error: {str(e)}")
            return None
