"""
Bookings API class for handling all bookings endpoint operations.
"""

from typing import Dict, Any
import requests
from .base_api import BaseAPI


class BookingsAPI(BaseAPI):
    """API class specifically for bookings endpoint operations."""
    
    def __init__(self, base_url: str, auth_token: str, timeout: int = 30, retry_count: int = 3):
        """
        Initialize BookingsAPI.
        
        Args:
            base_url: Base URL for the API
            auth_token: Authentication token
            timeout: Request timeout in seconds
            retry_count: Number of retries for failed requests
        """
        super().__init__(base_url, auth_token, timeout, retry_count)
        self.endpoint_base = '/bookings'
    
    def get_booking(self, booking_id: str) -> requests.Response:
        """
        Get booking by ID.
        
        Args:
            booking_id: The booking ID to retrieve
            
        Returns:
            requests.Response: HTTP response object
        """
        endpoint = f'{self.endpoint_base}/{booking_id}'
        return self.get(endpoint)
    
    def create_booking(self, booking_data: Dict[str, Any]) -> requests.Response:
        """
        Create new booking.
        
        Args:
            booking_data: Dictionary containing booking data
            
        Returns:
            requests.Response: HTTP response object
        """
        return self.post(self.endpoint_base, json_data=booking_data)
    
    def update_booking(self, booking_id: str, booking_data: Dict[str, Any]) -> requests.Response:
        """
        Update existing booking.
        
        Args:
            booking_id: The booking ID to update
            booking_data: Dictionary containing updated booking data
            
        Returns:
            requests.Response: HTTP response object
        """
        endpoint = f'{self.endpoint_base}/{booking_id}'
        return self.put(endpoint, json_data=booking_data)
    
    def cancel_booking(self, booking_id: str) -> requests.Response:
        """
        Cancel booking by ID.
        
        Args:
            booking_id: The booking ID to cancel
            
        Returns:
            requests.Response: HTTP response object
        """
        endpoint = f'{self.endpoint_base}/{booking_id}'
        return self.delete(endpoint)
    
    def get_bookings_list(self, params: Dict[str, Any] = None) -> requests.Response:
        """
        Get list of bookings with optional filtering.
        
        Args:
            params: Optional query parameters for filtering
            
        Returns:
            requests.Response: HTTP response object
        """
        return self.get(self.endpoint_base, params=params)
    
    def validate_booking_data(self, booking_data: Dict[str, Any]) -> bool:
        """
        Validate booking data structure.
        
        Args:
            booking_data: Booking data to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = ['customerId', 'productType', 'bookingDate']
        return all(field in booking_data for field in required_fields)
    
    def create_sample_booking_data(self, customer_id: str = "CUST001", 
                                   product_type: str = "CONSULTATION", 
                                   product_id: str = "PROD123456",
                                   booking_date: str = "2024-12-01",
                                   booking_time: str = "10:00") -> Dict[str, Any]:
        """
        Create sample booking data for testing.
        
        Args:
            customer_id: Customer ID
            product_type: Type of product/service to book
            product_id: Product ID
            booking_date: Date of the booking
            booking_time: Time of the booking
            
        Returns:
            Dict[str, Any]: Sample booking data
        """
        return {
            "customerId": customer_id,
            "productType": product_type,
            "productId": product_id,
            "bookingDate": booking_date,
            "bookingTime": booking_time,
            "branch": "Melbourne CBD"
        }