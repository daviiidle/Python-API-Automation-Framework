"""
Loans API class for handling all loans endpoint operations.
"""

from typing import Dict, Any
import requests
from .base_api import BaseAPI


class LoansAPI(BaseAPI):
    """API class specifically for loans endpoint operations."""
    
    def __init__(self, base_url: str, auth_token: str, timeout: int = 30, retry_count: int = 3):
        """
        Initialize LoansAPI.
        
        Args:
            base_url: Base URL for the API
            auth_token: Authentication token
            timeout: Request timeout in seconds
            retry_count: Number of retries for failed requests
        """
        super().__init__(base_url, auth_token, timeout, retry_count)
        self.endpoint_base = '/loans'
    
    def get_loan(self, loan_id: str) -> requests.Response:
        """
        Get loan by ID.
        
        Args:
            loan_id: The loan ID to retrieve
            
        Returns:
            requests.Response: HTTP response object
        """
        endpoint = f'{self.endpoint_base}/{loan_id}'
        return self.get(endpoint)
    
    def create_loan(self, loan_data: Dict[str, Any]) -> requests.Response:
        """
        Create new loan.
        
        Args:
            loan_data: Dictionary containing loan data
            
        Returns:
            requests.Response: HTTP response object
        """
        return self.post(self.endpoint_base, json_data=loan_data)
    
    def update_loan(self, loan_id: str, loan_data: Dict[str, Any]) -> requests.Response:
        """
        Update existing loan.
        
        Args:
            loan_id: The loan ID to update
            loan_data: Dictionary containing updated loan data
            
        Returns:
            requests.Response: HTTP response object
        """
        endpoint = f'{self.endpoint_base}/{loan_id}'
        return self.put(endpoint, json_data=loan_data)
    
    def delete_loan(self, loan_id: str) -> requests.Response:
        """
        Delete loan by ID.
        
        Args:
            loan_id: The loan ID to delete
            
        Returns:
            requests.Response: HTTP response object
        """
        endpoint = f'{self.endpoint_base}/{loan_id}'
        return self.delete(endpoint)
    
    def get_loans_list(self, params: Dict[str, Any] = None) -> requests.Response:
        """
        Get list of loans with optional filtering.
        
        Args:
            params: Optional query parameters for filtering
            
        Returns:
            requests.Response: HTTP response object
        """
        return self.get(self.endpoint_base, params=params)
    
    def validate_loan_data(self, loan_data: Dict[str, Any]) -> bool:
        """
        Validate loan data structure.
        
        Args:
            loan_data: Loan data to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = ['customerId', 'loanType', 'amount', 'term']
        return all(field in loan_data for field in required_fields)
    
    def create_sample_loan_data(self, customer_id: str = "CUST001", 
                                loan_type: str = "PERSONAL", 
                                amount: float = 25000.0,
                                term: int = 36,
                                interest_rate: float = 8.5) -> Dict[str, Any]:
        """
        Create sample loan data for testing.
        
        Args:
            customer_id: Customer ID
            loan_type: Type of loan (PERSONAL, HOME, CAR, etc.)
            amount: Loan amount
            term: Loan term in months
            interest_rate: Interest rate percentage
            
        Returns:
            Dict[str, Any]: Sample loan data
        """
        return {
            "customerId": customer_id,
            "loanType": loan_type,
            "amount": amount,
            "term": term,
            "termMonths": term,
            "interestRate": interest_rate
        }