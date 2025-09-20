"""
Health API class for handling all health check endpoint operations.
"""

from typing import Dict, Any
import requests
from .base_api import BaseAPI


class HealthAPI(BaseAPI):
    """API class specifically for health check endpoint operations."""
    
    def __init__(self, base_url: str, auth_token: str, timeout: int = 30, retry_count: int = 3):
        """
        Initialize HealthAPI.
        
        Args:
            base_url: Base URL for the API
            auth_token: Authentication token
            timeout: Request timeout in seconds
            retry_count: Number of retries for failed requests
        """
        super().__init__(base_url, auth_token, timeout, retry_count)
        self.endpoint_base = '/health'
    
    def get_health_status(self) -> requests.Response:
        """
        Get health status of the API.
        
        Returns:
            requests.Response: HTTP response object
        """
        return self.get(self.endpoint_base)
    
    def get_health_check(self) -> requests.Response:
        """
        Perform basic health check.
        
        Returns:
            requests.Response: HTTP response object
        """
        return self.get_health_status()
    
    def ping(self) -> requests.Response:
        """
        Simple ping to check API availability.
        
        Returns:
            requests.Response: HTTP response object
        """
        return self.get(f'{self.endpoint_base}/ping')
    
    def get_api_version(self) -> requests.Response:
        """
        Get API version information.
        
        Returns:
            requests.Response: HTTP response object
        """
        return self.get(f'{self.endpoint_base}/version')
    
    def get_readiness_probe(self) -> requests.Response:
        """
        Check if the API is ready to serve requests.
        
        Returns:
            requests.Response: HTTP response object
        """
        return self.get(f'{self.endpoint_base}/ready')
    
    def get_liveness_probe(self) -> requests.Response:
        """
        Check if the API is alive and responsive.
        
        Returns:
            requests.Response: HTTP response object
        """
        return self.get(f'{self.endpoint_base}/live')
    
    def is_api_healthy(self) -> bool:
        """
        Check if the API is healthy based on health endpoint response.
        
        Returns:
            bool: True if API is healthy, False otherwise
        """
        try:
            response = self.get_health_status()
            return response.status_code == 200
        except Exception:
            return False
    
    def get_health_metrics(self) -> Dict[str, Any]:
        """
        Get health metrics from the last health check response.
        
        Returns:
            Dict[str, Any]: Health metrics or empty dict if no valid response
        """
        try:
            response_json = self.get_last_response_json()
            if response_json:
                return response_json
            return {}
        except Exception:
            return {}