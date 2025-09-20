"""
Term Deposits API class for handling all term deposits endpoint operations.
"""

from typing import Dict, Any
import requests
from .base_api import BaseAPI


class TermDepositsAPI(BaseAPI):
    """API class specifically for term deposits endpoint operations."""
    
    def __init__(self, base_url: str, auth_token: str, timeout: int = 30, retry_count: int = 3):
        """
        Initialize TermDepositsAPI.
        
        Args:
            base_url: Base URL for the API
            auth_token: Authentication token
            timeout: Request timeout in seconds
            retry_count: Number of retries for failed requests
        """
        super().__init__(base_url, auth_token, timeout, retry_count)
        self.endpoint_base = '/term-deposits'
    
    def get_term_deposit(self, deposit_id: str) -> requests.Response:
        """
        Get term deposit by ID.
        
        Args:
            deposit_id: The term deposit ID to retrieve
            
        Returns:
            requests.Response: HTTP response object
        """
        endpoint = f'{self.endpoint_base}/{deposit_id}'
        return self.get(endpoint)
    
    def create_term_deposit(self, deposit_data: Dict[str, Any]) -> requests.Response:
        """
        Create new term deposit.
        
        Args:
            deposit_data: Dictionary containing term deposit data
            
        Returns:
            requests.Response: HTTP response object
        """
        return self.post(self.endpoint_base, json_data=deposit_data)
    
    def update_term_deposit(self, deposit_id: str, deposit_data: Dict[str, Any]) -> requests.Response:
        """
        Update existing term deposit.
        
        Args:
            deposit_id: The term deposit ID to update
            deposit_data: Dictionary containing updated term deposit data
            
        Returns:
            requests.Response: HTTP response object
        """
        endpoint = f'{self.endpoint_base}/{deposit_id}'
        return self.put(endpoint, json_data=deposit_data)
    
    def delete_term_deposit(self, deposit_id: str) -> requests.Response:
        """
        Delete term deposit by ID.
        
        Args:
            deposit_id: The term deposit ID to delete
            
        Returns:
            requests.Response: HTTP response object
        """
        endpoint = f'{self.endpoint_base}/{deposit_id}'
        return self.delete(endpoint)
    
    def get_term_deposits_list(self, params: Dict[str, Any] = None) -> requests.Response:
        """
        Get list of term deposits with optional filtering.
        
        Args:
            params: Optional query parameters for filtering
            
        Returns:
            requests.Response: HTTP response object
        """
        return self.get(self.endpoint_base, params=params)
    
    def validate_term_deposit_data(self, deposit_data: Dict[str, Any]) -> bool:
        """
        Validate term deposit data structure.
        
        Args:
            deposit_data: Term deposit data to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = ['customerId', 'amount', 'term', 'interestRate']
        return all(field in deposit_data for field in required_fields)
    
    def create_sample_term_deposit_data(self, customer_id: str = "CUST001", 
                                        amount: float = 10000.0,
                                        term: int = 12,
                                        interest_rate: float = 3.5,
                                        currency: str = "AUD") -> Dict[str, Any]:
        """
        Create sample term deposit data for testing.
        
        Args:
            customer_id: Customer ID
            amount: Deposit amount
            term: Term in months
            interest_rate: Interest rate percentage
            currency: Currency code
            
        Returns:
            Dict[str, Any]: Sample term deposit data
        """
        return {
            "customerId": customer_id,
            "amount": amount,
            "term": term,
            "termMonths": term,
            "interestRate": interest_rate,
            "currency": currency,
            "compoundingFrequency": "MONTHLY"
        }