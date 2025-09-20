"""
Accounts API class for handling all accounts endpoint operations.
"""

from typing import Dict, Any
import requests
from .base_api import BaseAPI


class AccountsAPI(BaseAPI):
    """API class specifically for accounts endpoint operations."""
    
    def __init__(self, base_url: str, auth_token: str, timeout: int = 30, retry_count: int = 3):
        """
        Initialize AccountsAPI.
        
        Args:
            base_url: Base URL for the API
            auth_token: Authentication token
            timeout: Request timeout in seconds
            retry_count: Number of retries for failed requests
        """
        super().__init__(base_url, auth_token, timeout, retry_count)
        self.endpoint_base = '/accounts'
    
    def get_account(self, account_id: str) -> requests.Response:
        """
        Get account by ID.
        
        Args:
            account_id: The account ID to retrieve
            
        Returns:
            requests.Response: HTTP response object
        """
        endpoint = f'{self.endpoint_base}/{account_id}'
        return self.get(endpoint)
    
    def create_account(self, account_data: Dict[str, Any]) -> requests.Response:
        """
        Create new account.
        
        Args:
            account_data: Dictionary containing account data
            
        Returns:
            requests.Response: HTTP response object
        """
        return self.post(self.endpoint_base, json_data=account_data)
    
    def update_account(self, account_id: str, account_data: Dict[str, Any]) -> requests.Response:
        """
        Update existing account.
        
        Args:
            account_id: The account ID to update
            account_data: Dictionary containing updated account data
            
        Returns:
            requests.Response: HTTP response object
        """
        endpoint = f'{self.endpoint_base}/{account_id}'
        return self.put(endpoint, json_data=account_data)
    
    def delete_account(self, account_id: str) -> requests.Response:
        """
        Delete account by ID.
        
        Args:
            account_id: The account ID to delete
            
        Returns:
            requests.Response: HTTP response object
        """
        endpoint = f'{self.endpoint_base}/{account_id}'
        return self.delete(endpoint)
    
    def get_accounts_list(self, params: Dict[str, Any] = None) -> requests.Response:
        """
        Get list of accounts with optional filtering.
        
        Args:
            params: Optional query parameters for filtering
            
        Returns:
            requests.Response: HTTP response object
        """
        return self.get(self.endpoint_base, params=params)
    
    def validate_account_data(self, account_data: Dict[str, Any]) -> bool:
        """
        Validate account data structure.
        
        Args:
            account_data: Account data to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = ['customerId', 'accountType', 'currency']
        return all(field in account_data for field in required_fields)
    
    def create_sample_account_data(self, customer_id: str = "CUST001", 
                                   account_type: str = "SAVINGS", 
                                   currency: str = "AUD",
                                   initial_balance: float = 1000.0) -> Dict[str, Any]:
        """
        Create sample account data for testing.
        
        Args:
            customer_id: Customer ID
            account_type: Type of account (SAVINGS, CHECKING, etc.)
            currency: Currency code
            initial_balance: Initial balance amount
            
        Returns:
            Dict[str, Any]: Sample account data
        """
        return {
            "customerId": customer_id,
            "accountType": account_type,
            "currency": currency,
            "initialBalance": initial_balance
        }