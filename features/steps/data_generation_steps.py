"""
Data generation step definitions for Banking API BDD tests.
Handles dynamic test data generation using Faker and data creation scenarios.
"""

import json
import requests
import time
from typing import Dict, Any
from decimal import Decimal
import random
from datetime import datetime, timedelta

from behave import given, when, then, step
from behave.runner import Context
from faker import Faker


# ============================================================================
# Dynamic Data Generation Steps
# ============================================================================

@given('I generate test data for "{data_type}"')
def step_generate_test_data(context: Context, data_type: str):
    """Generate dynamic test data using Faker for specified type."""
    # Ensure logger is available - fallback if environment.py didn't run
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    if not hasattr(context, 'test_data'):
        context.test_data = {}
    
    if not hasattr(context, 'faker'):
        context.faker = Faker('en_AU')  # Australian locale for banking data
    
    context.logger.info(f"[DATA] Generating dynamic test data for: {data_type}")
    
    # Generate dynamic data using Faker
    fake = context.faker
    
    # Generate a dynamic customer ID that will be reused across related records
    if not hasattr(context, 'generated_customer_id'):
        context.generated_customer_id = f"CUST{fake.unique.random_number(digits=6)}"
    
    sample_data = {
        'customer': {
            'firstName': fake.first_name(),
            'lastName': fake.last_name(),
            'email': fake.unique.email(),
            'phone': f'+61{fake.random_int(min=400000000, max=499999999)}',
            'dob': fake.date_of_birth(minimum_age=18, maximum_age=80).strftime('%Y-%m-%d'),
            'address': fake.street_address(),
            'city': fake.city(),
            'state': fake.random_element(['NSW', 'VIC', 'QLD', 'WA', 'SA', 'TAS', 'NT', 'ACT']),
            'postcode': fake.postcode()
        },
        'account': {
            'customerId': getattr(context, 'saved_variables', {}).get('customer_id', context.generated_customer_id),
            'accountType': fake.random_element(['SAVINGS', 'CHECKING', 'TERM_DEPOSIT']),
            'currency': fake.random_element(['AUD', 'USD', 'EUR']),
            'initialBalance': round(fake.random.uniform(100.00, 50000.00), 2)
        },
        'booking': {
            'customerId': getattr(context, 'saved_variables', {}).get('customer_id', context.generated_customer_id),
            'productType': fake.random_element(['APPOINTMENT', 'CONSULTATION', 'MEETING']),
            'productId': f"PROD{fake.random_number(digits=6)}",
            'serviceType': fake.random_element(['APPOINTMENT', 'CONSULTATION', 'MEETING']),
            'bookingDate': fake.future_date(end_date='+30d').strftime('%Y-%m-%d'),
            'bookingTime': fake.time(pattern='%H:%M'),
            'description': fake.sentence(nb_words=6)
        },
        'loan': {
            'customerId': getattr(context, 'saved_variables', {}).get('customer_id', context.generated_customer_id),
            'loanType': fake.random_element(['PERSONAL', 'HOME', 'CAR', 'BUSINESS']),
            'amount': round(fake.random.uniform(5000.00, 500000.00), 2),
            'termMonths': fake.random_element([12, 24, 36, 48, 60, 84, 120, 240, 300]),
            'interestRate': round(fake.random.uniform(3.5, 12.5), 2),
            'purpose': fake.sentence(nb_words=8)
        },
        'term_deposit': {
            'customerId': getattr(context, 'saved_variables', {}).get('customer_id', context.generated_customer_id),
            'principal': round(fake.random.uniform(1000.00, 100000.00), 2),
            'termMonths': fake.random_element([3, 6, 9, 12, 18, 24, 36, 48, 60]),
            'interestRate': round(fake.random.uniform(2.5, 8.5), 2),
            'compoundingFrequency': fake.random_element(['MONTHLY', 'QUARTERLY', 'ANNUALLY'])
        }
    }
    
    generated_data = sample_data.get(data_type, {})
    context.test_data[data_type] = generated_data
    
    # Log some key generated values for debugging
    context.logger.debug(f"[DATA] Generated {data_type} data: {json.dumps(generated_data, indent=2, default=str)}")
    if data_type == 'customer' and 'email' in generated_data:
        context.logger.info(f"[DATA] Generated customer email: {generated_data['email']}")
    elif 'customerId' in generated_data:
        context.logger.info(f"[DATA] Using customer ID: {generated_data['customerId']}")


@given('I generate a unique booking conflict test dataset')
def step_generate_booking_conflict_dataset(context: Context):
    """Generate dynamic booking conflict test data using timestamp for uniqueness."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)

    if not hasattr(context, 'faker'):
        context.faker = Faker('en_AU')

    # Use predictable test customer ID that WireMock can map to
    # This avoids conflicts with existing hardcoded data while remaining predictable
    context.conflict_booking_data = {
        'customerId': 'CUST_TEST_CONFLICT',
        'productType': 'CONSULTATION',
        'bookingDate': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
        'bookingTime': '10:00',
        'branch': 'Test Branch Dynamic'
    }

    context.logger.info(f"[DATA] Generated unique conflict booking dataset: customerId={context.conflict_booking_data['customerId']}")
    context.logger.debug(f"[DATA] Conflict booking data: {json.dumps(context.conflict_booking_data, indent=2)}")


@given('I generate a unique account conflict test dataset')
def step_generate_account_conflict_dataset(context: Context):
    """Generate dynamic account conflict test data using timestamp for uniqueness."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)

    if not hasattr(context, 'faker'):
        context.faker = Faker('en_AU')

    # Use predictable test customer ID that WireMock can map to
    # This avoids conflicts with existing hardcoded data while remaining predictable
    context.conflict_account_data = {
        'customerId': 'CUST_TEST_ACCOUNT',
        'accountType': 'SAVINGS',
        'currency': 'AUD',
        'initialBalance': 1000.00
    }

    context.logger.info(f"[DATA] Generated unique account conflict dataset: customerId={context.conflict_account_data['customerId']}")
    context.logger.debug(f"[DATA] Conflict account data: {json.dumps(context.conflict_account_data, indent=2)}")


@given('I generate a unique customer ID for account creation')
def step_generate_unique_customer_id(context: Context):
    """Generate a unique customer ID for account creation tests."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)

    # Generate timestamp-based unique customer ID
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]  # Include milliseconds
    context.unique_customer_id = f'CUST_UNIQUE_{timestamp}'

    context.logger.info(f"[DATA] Generated unique customer ID: {context.unique_customer_id}")


@when('I create a booking using the conflict dataset')
def step_create_booking_with_conflict_data(context: Context):
    """Create a booking using the generated conflict test data."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)

    if not hasattr(context, 'conflict_booking_data'):
        context.logger.error("[ERROR] No conflict booking data available. Run 'I generate a unique booking conflict test dataset' first")
        raise ValueError("No conflict booking data available")

    endpoint = '/bookings'
    base_url = context.base_url
    headers = context.auth_headers.copy()
    timeout = context.request_timeout

    full_url = f"{base_url.rstrip('/')}{endpoint}"
    data = context.conflict_booking_data

    context.logger.info(f"[REQUEST] Creating booking using conflict dataset")
    context.logger.debug(f"[URL] Full URL: {full_url}")
    context.logger.debug(f"[BODY] Request Body: {json.dumps(data, indent=2)}")

    try:
        start_time = time.time()
        context.response = requests.post(full_url, headers=headers, json=data, timeout=timeout)
        response_time = time.time() - start_time

        # Update metrics
        if hasattr(context, 'test_metrics'):
            context.test_metrics['api_calls'] += 1
            context.test_metrics['total_response_time'] += response_time
        if hasattr(context, 'scenario_metrics'):
            context.scenario_metrics['api_calls'] += 1
            context.scenario_metrics['total_response_time'] += response_time

        context.last_response = context.response

        # Log response details
        context.logger.info(f"[RESPONSE] Create booking response: {context.response.status_code}")
        context.logger.info(f"[TIME] Response time: {response_time:.3f}s")

        if context.response.status_code >= 400:
            context.logger.warning(f"[WARNING] HTTP error: {context.response.text}")

    except requests.exceptions.Timeout:
        context.logger.error(f"[ERROR] Request timeout after {timeout}s")
        raise
    except requests.exceptions.RequestException as e:
        context.logger.error(f"[ERROR] Request failed: {e}")
        raise


@when('I create an account using the conflict dataset')
def step_create_account_with_conflict_data(context: Context):
    """Create an account using the generated conflict test data."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)

    if not hasattr(context, 'conflict_account_data'):
        context.logger.error("[ERROR] No conflict account data available. Run 'I generate a unique account conflict test dataset' first")
        raise ValueError("No conflict account data available")

    endpoint = '/accounts'
    base_url = context.base_url
    headers = context.auth_headers.copy()
    timeout = context.request_timeout

    full_url = f"{base_url.rstrip('/')}{endpoint}"
    data = context.conflict_account_data

    context.logger.info(f"[REQUEST] Creating account using conflict dataset")
    context.logger.debug(f"[URL] Full URL: {full_url}")
    context.logger.debug(f"[BODY] Request Body: {json.dumps(data, indent=2)}")

    try:
        start_time = time.time()
        context.response = requests.post(full_url, headers=headers, json=data, timeout=timeout)
        response_time = time.time() - start_time

        # Update metrics
        if hasattr(context, 'test_metrics'):
            context.test_metrics['api_calls'] += 1
            context.test_metrics['total_response_time'] += response_time
        if hasattr(context, 'scenario_metrics'):
            context.scenario_metrics['api_calls'] += 1
            context.scenario_metrics['total_response_time'] += response_time

        context.last_response = context.response

        # Log response details
        context.logger.info(f"[RESPONSE] Create account response: {context.response.status_code}")
        context.logger.info(f"[TIME] Response time: {response_time:.3f}s")

        if context.response.status_code >= 400:
            context.logger.warning(f"[WARNING] HTTP error: {context.response.text}")

    except requests.exceptions.Timeout:
        context.logger.error(f"[ERROR] Request timeout after {timeout}s")
        raise
    except requests.exceptions.RequestException as e:
        context.logger.error(f"[ERROR] Request failed: {e}")
        raise


@given('I generate {count:d} test records for "{data_type}"')
def step_generate_multiple_test_data(context: Context, count: int, data_type: str):
    """Generate multiple dynamic test records using Faker for load testing."""
    if not hasattr(context, 'test_data'):
        context.test_data = {}
    
    if not hasattr(context, 'faker'):
        context.faker = Faker('en_AU')  # Australian locale for banking data
    
    fake = context.faker
    
    # Generate multiple unique records
    records = []
    for i in range(count):
        if data_type == 'customer':
            record = {
                'firstName': fake.first_name(),
                'lastName': fake.last_name(),
                'email': fake.unique.email(),
                'phone': f'+61{fake.random_int(min=400000000, max=499999999)}',
                'dob': fake.date_of_birth(minimum_age=18, maximum_age=80).strftime('%Y-%m-%d'),
                'address': fake.street_address(),
                'city': fake.city(),
                'state': fake.random_element(['NSW', 'VIC', 'QLD', 'WA', 'SA', 'TAS', 'NT', 'ACT']),
                'postcode': fake.postcode()
            }
        elif data_type == 'account':
            record = {
                'customerId': f"CUST{fake.unique.random_number(digits=6)}",
                'accountType': fake.random_element(['SAVINGS', 'CHECKING', 'TERM_DEPOSIT']),
                'currency': fake.random_element(['AUD', 'USD', 'EUR']),
                'initialBalance': round(fake.random.uniform(100.00, 50000.00), 2)
            }
        else:
            # Fallback for other types
            record = {
                'id': f"{data_type.upper()}{fake.unique.random_number(digits=6)}",
                'name': fake.name(),
                'value': fake.random.uniform(100, 10000)
            }
        
        records.append(record)
    
    context.test_data[f'{data_type}_list'] = records
    
    # Also create performance dataset for compatibility with performance steps
    if data_type == 'account':
        performance_data = []
        for i, record in enumerate(records):
            perf_item = {
                'customer': {
                    'firstName': f'PerfUser{i+1}',
                    'lastName': f'Test{i+1}',
                    'email': f'perf{i+1}@example.com',
                    'phone': f'+61400{i+1:06d}',
                    'dob': '1990-01-01'
                },
                'account': record,
                'correlation_id': f'perf_corr_{i+1:06d}'
            }
            performance_data.append(perf_item)
        context.performance_data = performance_data


# ============================================================================
# Invalid and Boundary Data Generation
# ============================================================================

@given('I generate invalid data for "{data_type}" with invalid "{field}"')
def step_generate_invalid_data(context: Context, data_type: str, field: str):
    """Generate invalid test data for negative testing."""
    if not hasattr(context, 'test_data'):
        context.test_data = {}
    
    # Generate invalid data for specified field
    base_data = {
        'customer': {
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '+61412345678',
            'dob': '1990-01-15'
        },
        'account': {
            'customerId': 'CUST001',
            'accountType': 'SAVINGS',
            'currency': 'AUD',
            'initialBalance': 1000.00
        }
    }.get(data_type, {})
    
    # Make specified field invalid
    invalid_data = base_data.copy()
    if field == 'email':
        invalid_data['email'] = 'invalid-email'
    elif field == 'phone':
        invalid_data['phone'] = 'invalid-phone'
    elif field == 'amount' or field == 'initialBalance':
        invalid_data[field] = -1000  # Negative amount
    elif field == 'customerId':
        invalid_data['customerId'] = ''  # Empty ID
    elif field == 'accountType':
        invalid_data['accountType'] = 'INVALID_TYPE'  # Invalid account type
    else:
        # For any other field, set it to null
        invalid_data[field] = None
    
    context.test_data[f'invalid_{data_type}'] = invalid_data


@given('I generate boundary data for "{data_type}" with "{boundary_type}" values')
def step_generate_boundary_data(context: Context, data_type: str, boundary_type: str):
    """Generate boundary condition test data."""
    if not hasattr(context, 'test_data'):
        context.test_data = {}
    
    # Generate boundary condition test data
    base_data = {
        'customer': {
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '+61412345678',
            'dob': '1990-01-15'
        },
        'account': {
            'customerId': 'CUST001',
            'accountType': 'SAVINGS',
            'currency': 'AUD',
            'initialBalance': 1000.00
        }
    }.get(data_type, {})
    
    boundary_data = base_data.copy()
    if boundary_type == 'min':
        if 'initialBalance' in boundary_data:
            boundary_data['initialBalance'] = 0.01  # Minimum balance
        if 'firstName' in boundary_data:
            boundary_data['firstName'] = 'A'  # Minimum name length
    elif boundary_type == 'max':
        if 'initialBalance' in boundary_data:
            boundary_data['initialBalance'] = 999999.99  # Maximum balance
        if 'firstName' in boundary_data:
            boundary_data['firstName'] = 'A' * 50  # Maximum name length
    
    context.test_data[f'boundary_{data_type}'] = boundary_data


# ============================================================================
# Resource Creation Using Generated Data
# ============================================================================

@when('I create a "{data_type}" using generated data')
def step_create_using_generated_data(context: Context, data_type: str):
    """Create resource using previously generated test data."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    if not hasattr(context, 'test_data'):
        context.logger.error(f"[ERROR] No test_data context available")
        raise ValueError(f"No test_data context available")
    
    # Check for exact match first, then check for boundary/invalid variations
    data = None
    if data_type in context.test_data:
        data = context.test_data[data_type]
    elif f'boundary_{data_type}' in context.test_data:
        data = context.test_data[f'boundary_{data_type}']
        context.logger.info(f"[INFO] Using boundary data for {data_type}")
    elif f'invalid_{data_type}' in context.test_data:
        data = context.test_data[f'invalid_{data_type}']
        context.logger.info(f"[INFO] Using invalid data for {data_type}")
    else:
        available_keys = list(context.test_data.keys())
        context.logger.error(f"[ERROR] No test data generated for {data_type}. Available keys: {available_keys}")
        raise ValueError(f"No test data generated for {data_type}. Available: {available_keys}")
    
    # Map data types to endpoints
    endpoints = {
        'customer': '/customers',
        'account': '/accounts',
        'booking': '/bookings',
        'loan': '/loans',
        'term_deposit': '/term-deposits'
    }
    
    if data_type not in endpoints:
        context.logger.error(f"[ERROR] Unknown data type: {data_type}")
        raise ValueError(f"Unknown data type: {data_type}")
    
    endpoint = endpoints[data_type]
    base_url = context.base_url
    headers = context.auth_headers.copy()
    timeout = context.request_timeout
    
    full_url = f"{base_url.rstrip('/')}{endpoint}"
    
    context.logger.info(f"[REQUEST] Creating {data_type} using generated data")
    context.logger.debug(f"[URL] Full URL: {full_url}")
    context.logger.debug(f"[BODY] Request Body: {json.dumps(data, indent=2)}")
    
    try:
        start_time = time.time()
        context.response = requests.post(full_url, headers=headers, json=data, timeout=timeout)
        response_time = time.time() - start_time
        
        # Update metrics
        if hasattr(context, 'test_metrics'):
            context.test_metrics['api_calls'] += 1
            context.test_metrics['total_response_time'] += response_time
        if hasattr(context, 'scenario_metrics'):
            context.scenario_metrics['api_calls'] += 1
            context.scenario_metrics['total_response_time'] += response_time
        
        context.last_response = context.response
        
        # Log response details
        context.logger.info(f"[RESPONSE] Create {data_type} Response: {context.response.status_code}")
        context.logger.info(f"[TIME]  Response Time: {response_time:.3f}s")
        
        # Store created resource ID if available
        try:
            if context.response.status_code in [200, 201] and context.response.headers.get('content-type', '').startswith('application/json'):
                response_json = context.response.json()
                id_field = f"{data_type}Id"
                if id_field in response_json:
                    if not hasattr(context, 'created_resources'):
                        context.created_resources = {}
                    context.created_resources[data_type] = response_json[id_field]
                    context.logger.debug(f"[BODY] Stored created {data_type} ID: {response_json[id_field]}")
        except Exception as e:
            context.logger.warning(f"[WARNING] Could not extract {data_type} ID from response: {e}")
        
    except requests.exceptions.Timeout:
        context.logger.error(f"[TIMEOUT] Create {data_type} request timed out")
        context.last_error = f"Create {data_type} request timed out"
        raise AssertionError(f"Request timeout")
    except Exception as e:
        context.logger.error(f"[ERROR] Create {data_type} request failed: {e}")
        context.last_error = str(e)
        raise AssertionError(f"Request failed: {e}")


@when('I retrieve the created "{data_type}" using generated ID')
def step_retrieve_using_generated_id(context: Context, data_type: str):
    """Retrieve resource using ID from generated test data."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    # Get the ID from stored created resources or last response
    resource_id = None
    
    if hasattr(context, 'created_resources') and data_type in context.created_resources:
        resource_id = context.created_resources[data_type]
    elif hasattr(context, 'response') and context.response:
        try:
            last_response = context.response.json()
            id_field = f"{data_type}Id"
            if id_field in last_response:
                resource_id = last_response[id_field]
        except Exception:
            pass
    
    if not resource_id:
        context.logger.error(f"[ERROR] No {data_type} ID available for retrieval")
        raise ValueError(f"No {data_type} ID available for retrieval")
    
    # Map data types to endpoints
    endpoints = {
        'customer': f'/customers/{resource_id}',
        'account': f'/accounts/{resource_id}',
        'booking': f'/bookings/{resource_id}',
        'loan': f'/loans/{resource_id}',
        'term_deposit': f'/term-deposits/{resource_id}'
    }
    
    if data_type not in endpoints:
        context.logger.error(f"[ERROR] Unknown data type for retrieval: {data_type}")
        raise ValueError(f"Unknown data type: {data_type}")
    
    endpoint = endpoints[data_type]
    base_url = context.base_url
    headers = context.auth_headers.copy()
    timeout = context.request_timeout
    
    full_url = f"{base_url.rstrip('/')}{endpoint}"
    
    context.logger.info(f"[VERIFY] Retrieving {data_type} with ID: {resource_id}")
    context.logger.debug(f"[URL] Full URL: {full_url}")
    
    try:
        start_time = time.time()
        context.response = requests.get(full_url, headers=headers, timeout=timeout)
        response_time = time.time() - start_time
        
        # Update metrics
        if hasattr(context, 'test_metrics'):
            context.test_metrics['api_calls'] += 1
            context.test_metrics['total_response_time'] += response_time
        if hasattr(context, 'scenario_metrics'):
            context.scenario_metrics['api_calls'] += 1
            context.scenario_metrics['total_response_time'] += response_time
        
        context.last_response = context.response
        
        # Log response details
        context.logger.info(f"[RESPONSE] Retrieve {data_type} Response: {context.response.status_code}")
        context.logger.info(f"[TIME]  Response Time: {response_time:.3f}s")
        
    except requests.exceptions.Timeout:
        context.logger.error(f"[TIMEOUT] Retrieve {data_type} request timed out")
        context.last_error = f"Retrieve {data_type} request timed out"
        raise AssertionError(f"Request timeout")
    except Exception as e:
        context.logger.error(f"[ERROR] Retrieve {data_type} request failed: {e}")
        context.last_error = str(e)
        raise AssertionError(f"Request failed: {e}")


# ============================================================================
# Data Validation Steps
# ============================================================================

@then('the response should contain generated "{field}" value')
def step_verify_generated_field(context: Context, field: str):
    """Verify that response contains the value from generated test data."""
    if not hasattr(context, 'test_data'):
        raise ValueError("No test data available for verification")
    
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    if not hasattr(context, 'response') or not context.response:
        context.logger.error(f"[ERROR] No response available for field verification")
        raise ValueError("No response available for field verification")
    
    try:
        response_json = context.response.json()
        context.logger.debug(f"[VERIFY] Verifying field '{field}' in response")
    except Exception as e:
        context.logger.error(f"[ERROR] Response is not valid JSON: {e}")
        raise ValueError("Response is not valid JSON")
    
    # Find the field in test data
    generated_value = None
    for data_type, data in context.test_data.items():
        if isinstance(data, dict) and field in data:
            generated_value = data[field]
            break
    
    assert generated_value is not None, f"Field '{field}' not found in generated test data"
    assert field in response_json, f"Field '{field}' not found in response"
    assert response_json[field] == generated_value, \
        f"Expected {generated_value}, got {response_json[field]}"


@then('the generated data should be realistic and valid')
def step_verify_data_realism(context: Context):
    """Verify that generated data follows realistic patterns."""
    if not hasattr(context, 'test_data'):
        raise ValueError("No test data available for verification")
    
    for data_type, data in context.test_data.items():
        if isinstance(data, dict):
            # Verify email format
            if 'email' in data:
                assert '@' in data['email'], f"Invalid email format: {data['email']}"
            
            # Verify phone format
            if 'phone' in data:
                assert data['phone'].startswith('+'), f"Invalid phone format: {data['phone']}"
            
            # Verify positive amounts
            if 'amount' in data or 'initialBalance' in data:
                amount = data.get('amount') or data.get('initialBalance')
                assert amount >= 0, f"Amount should be non-negative: {amount}"
            
            # Verify date formats
            if 'dob' in data:
                assert len(data['dob']) == 10, f"Invalid date format: {data['dob']}"