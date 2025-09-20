"""
Base API class providing common HTTP functionality for all endpoint-specific API classes.
"""

import time
import json
import logging
from typing import Dict, Any, Optional
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class BaseAPI:
    """Base API class with common HTTP functionality for all endpoints."""
    
    def __init__(self, base_url: str, auth_token: str, timeout: int = 30, retry_count: int = 3):
        """
        Initialize base API client.
        
        Args:
            base_url: Base URL for the API
            auth_token: Authentication token
            timeout: Request timeout in seconds
            retry_count: Number of retries for failed requests
        """
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.timeout = timeout
        self.retry_count = retry_count
        
        # Initialize session with retry strategy
        self.session = requests.Session()
        self._setup_retry_strategy()
        
        # Request/Response tracking
        self.last_request = None
        self.last_response = None
        self.last_response_time = None
        
        # Logging
        self.logger = logging.getLogger(__name__)
        
    def _setup_retry_strategy(self) -> None:
        """Setup retry strategy for HTTP requests."""
        retry_strategy = Retry(
            total=self.retry_count,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def set_correlation_id(self, correlation_id: str) -> None:
        """Set correlation ID for request tracking."""
        self.session.headers.update({'X-Correlation-Id': correlation_id})
    
    def reset_session(self) -> None:
        """Reset session headers and state."""
        self.session.headers.clear()
        self.session.headers.update(self._get_default_headers())
    
    def close_session(self) -> None:
        """Close the session."""
        self.session.close()
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for requests."""
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.auth_token}',
            'User-Agent': 'Banking-API-BDD-Tests/1.0'
        }
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint."""
        return urljoin(self.base_url + '/', endpoint.lstrip('/'))
    
    def _log_request(self, method: str, url: str, **kwargs) -> None:
        """Log HTTP request details."""
        self.logger.info(f"→ {method.upper()} {url}")
        if kwargs.get('headers'):
            # Don't log sensitive headers
            safe_headers = {k: v for k, v in kwargs['headers'].items() 
                          if k.lower() not in ['authorization', 'x-api-key']}
            self.logger.debug(f"  Headers: {safe_headers}")
        if kwargs.get('json'):
            self.logger.debug(f"  Body: {json.dumps(kwargs['json'], indent=2)}")
    
    def _log_response(self, response: requests.Response, response_time: float) -> None:
        """Log HTTP response details."""
        self.logger.info(f"← {response.status_code} {response.reason} ({response_time:.3f}s)")
        self.logger.debug(f"  Response Headers: {dict(response.headers)}")
        if response.text:
            try:
                response_json = response.json()
                self.logger.debug(f"  Response Body: {json.dumps(response_json, indent=2)}")
            except json.JSONDecodeError:
                self.logger.debug(f"  Response Body: {response.text[:500]}...")
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Make HTTP request with error handling and logging.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            **kwargs: Additional request parameters
            
        Returns:
            requests.Response: HTTP response object
        """
        url = self._build_url(endpoint)
        
        # Merge default headers with provided headers
        headers = self._get_default_headers()
        if kwargs.get('headers'):
            headers.update(kwargs['headers'])
        kwargs['headers'] = headers
        
        # Set timeout if not provided
        kwargs.setdefault('timeout', self.timeout)
        
        # Log request
        self._log_request(method, url, **kwargs)
        
        # Track request
        self.last_request = {
            'method': method,
            'url': url,
            'kwargs': kwargs
        }
        
        # Make request and track timing
        start_time = time.time()
        try:
            response = self.session.request(method, url, **kwargs)
            response_time = time.time() - start_time
            
            # Track response
            self.last_response = response
            self.last_response_time = response_time
            
            # Log response
            self._log_response(response, response_time)
            
            return response
            
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            self.logger.error(f"Request failed after {response_time:.3f}s: {e}")
            raise
    
    def get(self, endpoint: str, params: Dict[str, Any] = None, **kwargs) -> requests.Response:
        """Make GET request."""
        if params:
            kwargs['params'] = params
        return self._make_request('GET', endpoint, **kwargs)
    
    def post(self, endpoint: str, data: Dict[str, Any] = None, json_data: Dict[str, Any] = None, **kwargs) -> requests.Response:
        """Make POST request."""
        if json_data:
            kwargs['json'] = json_data
        elif data:
            kwargs['data'] = data
        return self._make_request('POST', endpoint, **kwargs)
    
    def put(self, endpoint: str, data: Dict[str, Any] = None, json_data: Dict[str, Any] = None, **kwargs) -> requests.Response:
        """Make PUT request."""
        if json_data:
            kwargs['json'] = json_data
        elif data:
            kwargs['data'] = data
        return self._make_request('PUT', endpoint, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """Make DELETE request."""
        return self._make_request('DELETE', endpoint, **kwargs)
    
    def patch(self, endpoint: str, data: Dict[str, Any] = None, json_data: Dict[str, Any] = None, **kwargs) -> requests.Response:
        """Make PATCH request."""
        if json_data:
            kwargs['json'] = json_data
        elif data:
            kwargs['data'] = data
        return self._make_request('PATCH', endpoint, **kwargs)
    
    def get_last_response_json(self) -> Optional[Dict[str, Any]]:
        """Get last response as JSON."""
        if self.last_response:
            try:
                return self.last_response.json()
            except json.JSONDecodeError:
                return None
        return None
    
    def assert_status_code(self, expected_status: int) -> None:
        """Assert that last response has expected status code."""
        if not self.last_response:
            raise AssertionError("No response to check")
        
        actual_status = self.last_response.status_code
        if actual_status != expected_status:
            raise AssertionError(
                f"Expected status code {expected_status}, but got {actual_status}. "
                f"Response: {self.last_response.text[:200]}..."
            )
    
    def assert_response_contains(self, key: str, expected_value: Any = None) -> None:
        """Assert that response JSON contains key with optional value check."""
        response_json = self.get_last_response_json()
        if not response_json:
            raise AssertionError("Response is not valid JSON")
        
        if key not in response_json:
            raise AssertionError(f"Response does not contain key '{key}'. Keys: {list(response_json.keys())}")
        
        if expected_value is not None and response_json[key] != expected_value:
            raise AssertionError(f"Expected '{key}' to be '{expected_value}', but got '{response_json[key]}'")
    
    def assert_response_time_under(self, max_time_ms: int) -> None:
        """Assert that last response time is under the specified threshold."""
        if not self.last_response_time:
            raise AssertionError("No response time to check")
        
        response_time_ms = self.last_response_time * 1000
        if response_time_ms > max_time_ms:
            raise AssertionError(
                f"Response time {response_time_ms:.2f}ms exceeds threshold of {max_time_ms}ms"
            )