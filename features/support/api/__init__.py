"""
API module for Banking API endpoint classes.
This module provides organized, endpoint-specific API classes for better separation of concerns.
"""

from .base_api import BaseAPI
from .accounts_api import AccountsAPI
from .customers_api import CustomersAPI
from .bookings_api import BookingsAPI
from .loans_api import LoansAPI
from .term_deposits_api import TermDepositsAPI
from .health_api import HealthAPI

__all__ = [
    'BaseAPI',
    'AccountsAPI',
    'CustomersAPI',
    'BookingsAPI',
    'LoansAPI',
    'TermDepositsAPI',
    'HealthAPI'
]