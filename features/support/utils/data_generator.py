"""
Data generation utilities using Faker for Banking API BDD tests.
Provides dynamic test data generation for all banking services.
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from faker import Faker


class BankingDataGenerator:
    """Generate realistic banking test data using Faker."""
    
    def __init__(self, locale: str = 'en_AU'):
        """Initialize with specific locale for Australian banking context."""
        self.faker = Faker(locale)
        Faker.seed(None)  # Random seed for each run
    
    def generate_customer_data(self, **overrides) -> Dict[str, Any]:
        """Generate customer data with optional field overrides."""
        data = {
            'firstName': self.faker.first_name(),
            'lastName': self.faker.last_name(),
            'email': self.faker.email(),
            'phone': f"+614{self.faker.random_number(digits=8, fix_len=True)}",
            'dob': self.faker.date_of_birth(minimum_age=18, maximum_age=85).isoformat(),
            'address': {
                'street': self.faker.street_address(),
                'city': self.faker.city(),
                'state': self.faker.state_abbr(),
                'postcode': self.faker.postcode(),
                'country': 'Australia'
            }
        }
        data.update(overrides)
        return data
    
    def generate_account_data(self, **overrides) -> Dict[str, Any]:
        """Generate account data with optional field overrides."""
        account_types = ['SAVINGS', 'CHECKING', 'TERM_DEPOSIT', 'CREDIT_CARD']
        currencies = ['AUD', 'USD', 'EUR', 'GBP']
        
        data = {
            'customerId': f"CUST{self.faker.random_number(digits=6, fix_len=True)}",
            'accountType': self.faker.random_element(account_types),
            'currency': self.faker.random_element(currencies),
            'initialBalance': round(self.faker.random.uniform(0, 100000), 2),
            'description': f"{self.faker.word().capitalize()} {self.faker.random_element(account_types).lower()} account",
            'branch': f"{self.faker.city()} {self.faker.random_element(['CBD', 'North', 'South', 'East', 'West'])}"
        }
        data.update(overrides)
        return data
    
    def generate_booking_data(self, **overrides) -> Dict[str, Any]:
        """Generate booking data with optional field overrides."""
        service_types = ['APPOINTMENT', 'CONSULTATION', 'LOAN_MEETING', 'INVESTMENT_ADVICE']
        booking_times = ['09:00', '10:00', '11:00', '14:00', '15:00', '16:00']
        
        # Generate future date within next 30 days
        future_date = self.faker.date_between(start_date='today', end_date='+30d')
        
        data = {
            'customerId': f"CUST{self.faker.random_number(digits=6, fix_len=True)}",
            'serviceType': self.faker.random_element(service_types),
            'bookingDate': future_date.isoformat(),
            'bookingTime': self.faker.random_element(booking_times),
            'branch': f"{self.faker.city()} Branch",
            'notes': self.faker.sentence()
        }
        data.update(overrides)
        return data
    
    def generate_loan_data(self, **overrides) -> Dict[str, Any]:
        """Generate loan data with optional field overrides."""
        loan_types = ['PERSONAL', 'HOME', 'CAR', 'BUSINESS']
        terms = [12, 24, 36, 48, 60, 120, 240, 360]  # months
        
        data = {
            'customerId': f"CUST{self.faker.random_number(digits=6, fix_len=True)}",
            'loanType': self.faker.random_element(loan_types),
            'amount': round(self.faker.random.uniform(5000, 500000), 2),
            'term': self.faker.random_element(terms),
            'interestRate': round(self.faker.random.uniform(3.5, 15.0), 2),
            'purpose': self.faker.sentence(),
            'employmentStatus': self.faker.random_element(['FULL_TIME', 'PART_TIME', 'SELF_EMPLOYED', 'UNEMPLOYED']),
            'annualIncome': round(self.faker.random.uniform(30000, 200000), 2)
        }
        data.update(overrides)
        return data
    
    def generate_term_deposit_data(self, **overrides) -> Dict[str, Any]:
        """Generate term deposit data with optional field overrides."""
        terms = [3, 6, 9, 12, 18, 24, 36, 48, 60]  # months
        
        data = {
            'customerId': f"CUST{self.faker.random_number(digits=6, fix_len=True)}",
            'amount': round(self.faker.random.uniform(1000, 100000), 2),
            'term': self.faker.random_element(terms),
            'interestRate': round(self.faker.random.uniform(2.0, 6.0), 2),
            'compoundingFrequency': self.faker.random_element(['MONTHLY', 'QUARTERLY', 'ANNUALLY']),
            'maturityInstructions': self.faker.random_element(['ROLLOVER', 'TRANSFER_TO_SAVINGS', 'CONTACT_CUSTOMER'])
        }
        data.update(overrides)
        return data
    
    def generate_invalid_data(self, data_type: str, invalid_field: str) -> Dict[str, Any]:
        """Generate invalid data for negative testing."""
        if data_type == 'customer':
            data = self.generate_customer_data()
        elif data_type == 'account':
            data = self.generate_account_data()
        elif data_type == 'booking':
            data = self.generate_booking_data()
        elif data_type == 'loan':
            data = self.generate_loan_data()
        elif data_type == 'term_deposit':
            data = self.generate_term_deposit_data()
        else:
            raise ValueError(f"Unknown data type: {data_type}")
        
        # Make specific field invalid
        if invalid_field in data:
            if invalid_field in ['email']:
                data[invalid_field] = 'invalid-email-format'
            elif invalid_field in ['phone']:
                data[invalid_field] = '123'  # Too short
            elif invalid_field in ['amount', 'initialBalance']:
                data[invalid_field] = -100  # Negative amount
            elif invalid_field in ['dob']:
                data[invalid_field] = '2025-01-01'  # Future date
            elif invalid_field in ['customerId', 'accountId']:
                data[invalid_field] = ''  # Empty string
            else:
                data[invalid_field] = None  # Null value
        
        return data
    
    def generate_boundary_data(self, data_type: str, boundary_type: str) -> Dict[str, Any]:
        """Generate boundary condition data for testing."""
        if data_type == 'customer':
            data = self.generate_customer_data()
            if boundary_type == 'min':
                data.update({
                    'firstName': 'A',
                    'lastName': 'B',
                    'phone': '+61400000000'
                })
            elif boundary_type == 'max':
                data.update({
                    'firstName': 'A' * 50,
                    'lastName': 'B' * 50,
                    'phone': '+614' + '9' * 9
                })
        elif data_type == 'account':
            data = self.generate_account_data()
            if boundary_type == 'min':
                data.update({
                    'initialBalance': 0.01,
                    'description': 'A'
                })
            elif boundary_type == 'max':
                data.update({
                    'initialBalance': 999999999.99,
                    'description': 'A' * 500
                })
        
        return data
    
    def generate_multiple_records(self, data_type: str, count: int) -> List[Dict[str, Any]]:
        """Generate multiple records of the same type."""
        generators = {
            'customer': self.generate_customer_data,
            'account': self.generate_account_data,
            'booking': self.generate_booking_data,
            'loan': self.generate_loan_data,
            'term_deposit': self.generate_term_deposit_data
        }
        
        if data_type not in generators:
            raise ValueError(f"Unknown data type: {data_type}")
        
        return [generators[data_type]() for _ in range(count)]
    
    def generate_correlation_id(self) -> str:
        """Generate a unique correlation ID for request tracking."""
        return f"test-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}"
    
    def generate_test_scenario_data(self, scenario_name: str) -> Dict[str, Any]:
        """Generate data specific to test scenarios."""
        scenarios = {
            'happy_path_customer': self.generate_customer_data,
            'happy_path_account': self.generate_account_data,
            'invalid_email_customer': lambda: self.generate_invalid_data('customer', 'email'),
            'negative_balance_account': lambda: self.generate_invalid_data('account', 'initialBalance'),
            'boundary_min_customer': lambda: self.generate_boundary_data('customer', 'min'),
            'boundary_max_account': lambda: self.generate_boundary_data('account', 'max'),
        }
        
        if scenario_name in scenarios:
            return scenarios[scenario_name]()
        else:
            # Default to generating customer data
            return self.generate_customer_data()
    
    def generate_performance_test_data(self, count: int = 100) -> List[Dict[str, Any]]:
        """Generate large dataset for performance testing."""
        return [
            {
                'customer': self.generate_customer_data(),
                'account': self.generate_account_data(),
                'correlation_id': self.generate_correlation_id()
            }
            for _ in range(count)
        ]


# Global instance for use in step definitions
data_generator = BankingDataGenerator()