"""Base integration class"""

import httpx
from typing import Optional, Dict, Any
from app.core.config import settings


class BaseAPIClient:
    """Base class for external API clients"""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: float = 30.0):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL for the API
            api_key: Optional API key
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make GET request to API.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response or None on error
        """
        try:
            url = f"{self.base_url}{endpoint}"
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e}")
            return None
        except Exception as e:
            print(f"Error making GET request: {e}")
            return None
    
    async def post(self, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make POST request to API.
        
        Args:
            endpoint: API endpoint path
            data: Request body data
            
        Returns:
            JSON response or None on error
        """
        try:
            url = f"{self.base_url}{endpoint}"
            response = await self.client.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e}")
            return None
        except Exception as e:
            print(f"Error making POST request: {e}")
            return None
    
    async def close(self):
        """Close HTTP client connection"""
        await self.client.aclose()
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

