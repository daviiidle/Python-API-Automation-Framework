"""
Customers API class for handling all customers endpoint operations.
"""

from typing import Dict, Any
import requests
from .base_api import BaseAPI


class CustomersAPI(BaseAPI):
    """API class specifically for customers endpoint operations."""
    
    def __init__(self, base_url: str, auth_token: str, timeout: int = 30, retry_count: int = 3):
        """
        Initialize CustomersAPI.
        
        Args:
            base_url: Base URL for the API
            auth_token: Authentication token
            timeout: Request timeout in seconds
            retry_count: Number of retries for failed requests
        """
        super().__init__(base_url, auth_token, timeout, retry_count)
        self.endpoint_base = '/customers'
    
    def get_customer(self, customer_id: str) -> requests.Response:
        """
        Get customer by ID.
        
        Args:
            customer_id: The customer ID to retrieve
            
        Returns:
            requests.Response: HTTP response object
        """
        endpoint = f'{self.endpoint_base}/{customer_id}'
        return self.get(endpoint)
    
    def create_customer(self, customer_data: Dict[str, Any]) -> requests.Response:
        """
        Create new customer.
        
        Args:
            customer_data: Dictionary containing customer data
            
        Returns:
            requests.Response: HTTP response object
        """
        return self.post(self.endpoint_base, json_data=customer_data)
    
    def update_customer(self, customer_id: str, customer_data: Dict[str, Any]) -> requests.Response:
        """
        Update existing customer.
        
        Args:
            customer_id: The customer ID to update
            customer_data: Dictionary containing updated customer data
            
        Returns:
            requests.Response: HTTP response object
        """
        endpoint = f'{self.endpoint_base}/{customer_id}'
        return self.put(endpoint, json_data=customer_data)
    
    def delete_customer(self, customer_id: str) -> requests.Response:
        """
        Delete customer by ID.
        
        Args:
            customer_id: The customer ID to delete
            
        Returns:
            requests.Response: HTTP response object
        """
        endpoint = f'{self.endpoint_base}/{customer_id}'
        return self.delete(endpoint)
    
    def get_customers_list(self, params: Dict[str, Any] = None) -> requests.Response:
        """
        Get list of customers with optional filtering.
        
        Args:
            params: Optional query parameters for filtering
            
        Returns:
            requests.Response: HTTP response object
        """
        return self.get(self.endpoint_base, params=params)
    
    def validate_customer_data(self, customer_data: Dict[str, Any]) -> bool:
        """
        Validate customer data structure.
        
        Args:
            customer_data: Customer data to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = ['firstName', 'lastName', 'email']
        return all(field in customer_data for field in required_fields)
    
    def create_sample_customer_data(self, first_name: str = "John", 
                                    last_name: str = "Doe", 
                                    email: str = "john.doe@example.com",
                                    phone: str = "+61412345678") -> Dict[str, Any]:
        """
        Create sample customer data for testing.
        
        Args:
            first_name: Customer first name
            last_name: Customer last name
            email: Customer email address
            phone: Customer phone number
            
        Returns:
            Dict[str, Any]: Sample customer data
        """
        return {
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "phone": phone,
            "dob": "1990-01-15",
            "address": "123 Main Street",
            "city": "Melbourne",
            "state": "VIC",
            "postcode": "3000"
        }