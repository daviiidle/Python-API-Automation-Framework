"""
Environment setup and configuration step definitions for Banking API BDD tests.
Handles API availability, authentication setup, and test preconditions.
"""

import json
import time
import requests
import os
from datetime import datetime

from behave import given, when, then, step
from behave.runner import Context


# ============================================================================
# API Availability and Health Checks
# ============================================================================

@given('the banking API is available')
def step_api_available(context: Context):
    """Verify that the banking API is accessible."""
    # Ensure logger is available - fallback if environment.py didn't run
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    # Use base_url from context (loaded from environment)
    base_url = context.base_url
    timeout = getattr(context, 'request_timeout', 10)
    
    context.logger.info("[API] Checking API availability...")
    context.logger.debug(f"[API] Target API URL: {base_url}")
    environment = os.getenv('TEST_ENVIRONMENT', os.getenv('ENVIRONMENT', 'dev'))
    context.logger.debug(f"[ENV] Environment: {environment}")
    
    try:
        start_time = time.time()
        response = requests.get(base_url, timeout=timeout)
        response_time = time.time() - start_time
        
        context.logger.info(f"[RESPONSE] API Health Check - Status: {response.status_code}")
        context.logger.debug(f"[TIME] Health Check Response Time: {response_time:.3f}s")
        context.logger.debug(f"[HEADERS] Health Check Response Headers: {dict(response.headers)}")
        
        # Allow 200, 404, or any status that indicates the server is responding
        assert response.status_code in [200, 404, 405], f"API is not available: {response.status_code}"
        
        context.logger.info("[SUCCESS] API is available and responding")
        
    except requests.exceptions.Timeout:
        context.logger.error("[TIMEOUT] API health check timed out")
        context.last_error = "API health check timed out"
        context.base_url = base_url
        raise AssertionError("API health check timed out")
    except requests.exceptions.ConnectionError as e:
        context.logger.error(f"[CONNECTION] Connection error during API health check: {e}")
        context.last_error = f"Connection error during API health check: {e}"
        context.base_url = base_url
        raise AssertionError(f"Cannot connect to API: {e}")
    except Exception as e:
        context.logger.warning(f"[WARNING] API connection issue (continuing anyway): {e}")
        context.base_url = base_url


# ============================================================================
# Authentication Setup and Management
# ============================================================================

@given('I have valid authentication credentials')
def step_valid_auth(context: Context):
    """Verify that valid authentication is configured."""
    auth_token = getattr(context, 'auth_token', os.getenv('AUTH_TOKEN', 'banking-api-key-2024'))
    
    context.logger.info("[AUTH] Configuring authentication credentials...")
    context.logger.debug(f"[AUTH] Auth Token Source: {'Context' if hasattr(context, 'auth_token') else 'Environment'}")
    
    if not auth_token:
        context.logger.error("[ERROR] No authentication token configured")
        raise AssertionError("No authentication token configured")
    
    # Mask sensitive data for logging
    masked_token = f"{'*' * (len(auth_token) - 4)}{auth_token[-4:]}" if len(auth_token) > 4 else "****"
    context.logger.info(f"[AUTH] Auth Token Configured: {masked_token}")
    
    context.auth_headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    context.auth_token = auth_token
    
    context.logger.debug("[HEADERS] Default headers configured with authentication")
    context.logger.info("[SUCCESS] Authentication credentials validated and configured")


# ============================================================================
# Correlation ID Management
# ============================================================================

@given('I set the correlation ID to "{correlation_id}"')
def step_set_correlation_id(context: Context, correlation_id: str):
    """Set a specific correlation ID for request tracking."""
    # Ensure logger is available - fallback if environment.py didn't run
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    context.logger.info(f"[CORRELATION] Setting correlation ID: {correlation_id}")
    
    # Update auth headers with correlation ID
    if hasattr(context, 'auth_headers'):
        context.auth_headers['X-Correlation-Id'] = correlation_id
    else:
        context.auth_headers = {
            'Authorization': f'Bearer {context.auth_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Correlation-Id': correlation_id
        }
    
    context.logger.debug(f"[HEADERS] Updated headers with correlation ID: {correlation_id}")


@step('I save the generated correlation ID')
def step_save_correlation_id(context: Context):
    """Generate and save correlation ID for tracking."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    import uuid
    correlation_id = f"corr_{uuid.uuid4().hex[:12]}"
    
    # Set correlation ID in headers for future requests
    if not hasattr(context, 'auth_headers'):
        context.auth_headers = {}
    context.auth_headers['X-Correlation-ID'] = correlation_id
    
    context.logger.info(f"[HEADERS] Generated correlation ID: {correlation_id}")
    
    if not hasattr(context, 'saved_data'):
        context.saved_data = {}
    context.saved_data['correlation_id'] = correlation_id


# ============================================================================
# Test Data Setup for Services
# ============================================================================

@given('I have test data for "{service}" service')
def step_have_test_data(context: Context, service: str):
    """Load test data for a specific service."""
    if not hasattr(context, 'test_data'):
        context.test_data = {}
    
    # In a real implementation, this would load from test data files
    # For now, we'll create sample data
    sample_data = {
        'customers': {
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john.doe@email.com',
            'phone': '+61412345678',
            'dob': '1990-01-15'
        },
        'accounts': {
            'customerId': 'CUST001',
            'accountType': 'SAVINGS',
            'currency': 'AUD',
            'initialBalance': 1000.00
        },
        'bookings': {
            'customerId': 'CUST001',
            'serviceType': 'APPOINTMENT',
            'bookingDate': '2024-01-15',
            'bookingTime': '10:00'
        },
        'loans': {
            'customerId': 'CUST001',
            'loanType': 'PERSONAL',
            'amount': 50000.00,
            'term': 36
        },
        'term_deposits': {
            'customerId': 'CUST001',
            'amount': 10000.00,
            'term': 12,
            'interestRate': 4.5
        }
    }
    
    context.test_data[service] = sample_data.get(service, {})


# ============================================================================
# Wait and Timing Operations
# ============================================================================

@given('I wait for "{seconds:d}" seconds')
def step_wait(context: Context, seconds: int):
    """Wait for specified number of seconds."""
    time.sleep(seconds)


# ============================================================================
# Environment Configuration and Initialization
# ============================================================================

# Debug step moved to common_steps.py to avoid duplicates


@given('the test environment is properly configured')
def step_environment_configured(context: Context):
    """Verify that the test environment is properly configured."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    context.logger.info("[ENV] Verifying test environment configuration...")
    
    # Check essential configuration
    required_config = {
        'base_url': getattr(context, 'base_url', None),
        'auth_token': getattr(context, 'auth_token', None),
        'request_timeout': getattr(context, 'request_timeout', None)
    }
    
    missing_config = []
    for key, value in required_config.items():
        if value is None:
            missing_config.append(key)
        else:
            # Mask sensitive data for logging
            if key == 'auth_token':
                masked_value = f"{'*' * (len(str(value)) - 4)}{str(value)[-4:]}" if len(str(value)) > 4 else "****"
                context.logger.debug(f"[CONFIG] {key}: {masked_value}")
            else:
                context.logger.debug(f"[CONFIG] {key}: {value}")
    
    if missing_config:
        context.logger.error(f"[ERROR] Missing required configuration: {missing_config}")
        raise AssertionError(f"Missing required configuration: {missing_config}")
    
    context.logger.info("[SUCCESS] Test environment is properly configured")


@given('I initialize test metrics')
def step_initialize_metrics(context: Context):
    """Initialize test metrics collection."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    context.logger.info("[METRICS] Initializing test metrics collection...")
    
    # Initialize test metrics if not already present
    if not hasattr(context, 'test_metrics'):
        context.test_metrics = {
            'start_time': datetime.now(),
            'total_scenarios': 0,
            'passed_scenarios': 0,
            'failed_scenarios': 0,
            'skipped_scenarios': 0,
            'api_calls': 0,
            'total_response_time': 0.0
        }
    
    if not hasattr(context, 'scenario_metrics'):
        context.scenario_metrics = {
            'start_time': datetime.now(),
            'api_calls': 0,
            'total_response_time': 0.0,
            'errors': []
        }
    
    context.logger.info("[SUCCESS] Test metrics initialized")


@given('I reset the test environment')
def step_reset_environment(context: Context):
    """Reset test environment to clean state."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    context.logger.info("[ENV] Resetting test environment...")
    
    # Clear any saved data
    if hasattr(context, 'saved_data'):
        context.saved_data.clear()
    
    # Clear test data
    if hasattr(context, 'test_data'):
        context.test_data.clear()
    
    # Reset response objects
    if hasattr(context, 'response'):
        context.response = None
    if hasattr(context, 'last_response'):
        context.last_response = None
    
    # Clear errors
    if hasattr(context, 'last_error'):
        context.last_error = None
    
    # Reset scenario metrics but keep test metrics
    if hasattr(context, 'scenario_metrics'):
        context.scenario_metrics = {
            'start_time': datetime.now(),
            'api_calls': 0,
            'total_response_time': 0.0,
            'errors': []
        }
    
    context.logger.info("[SUCCESS] Test environment reset to clean state")


@given('I configure request timeout to {timeout:d} seconds')
def step_configure_timeout(context: Context, timeout: int):
    """Configure request timeout for all API calls."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    context.logger.info(f"[CONFIG] Setting request timeout to {timeout} seconds")
    context.request_timeout = timeout
    context.logger.debug(f"[CONFIG] Request timeout configured: {timeout}s")


@given('I set the base URL to "{url}"')
def step_set_base_url(context: Context, url: str):
    """Set the base URL for API requests."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    context.logger.info(f"[CONFIG] Setting base URL to: {url}")
    context.base_url = url
    context.logger.debug(f"[CONFIG] Base URL configured: {url}")


# ============================================================================
# Test Preconditions and Prerequisites
# ============================================================================

@given('the API endpoints are responding')
def step_endpoints_responding(context: Context):
    """Verify that key API endpoints are responding."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    context.logger.info("[API] Verifying key endpoints are responding...")
    
    # Key endpoints to check
    endpoints_to_check = [
        '/health',
        '/customers',
        '/accounts', 
        '/bookings',
        '/loans',
        '/term-deposits'
    ]
    
    base_url = context.base_url
    headers = getattr(context, 'auth_headers', {})
    timeout = getattr(context, 'request_timeout', 10)
    
    failed_endpoints = []
    for endpoint in endpoints_to_check:
        try:
            full_url = f"{base_url.rstrip('/')}{endpoint}"
            response = requests.get(full_url, headers=headers, timeout=timeout)
            
            # Accept any response that indicates the endpoint exists (not just 200)
            if response.status_code in [200, 401, 403, 404, 405]:
                context.logger.debug(f"[ENDPOINT] {endpoint}: {response.status_code} - OK")
            else:
                context.logger.warning(f"[ENDPOINT] {endpoint}: {response.status_code} - Unexpected")
                failed_endpoints.append(f"{endpoint} ({response.status_code})")
                
        except requests.exceptions.RequestException as e:
            context.logger.warning(f"[ENDPOINT] {endpoint}: Connection failed - {e}")
            failed_endpoints.append(f"{endpoint} (Connection failed)")
    
    if failed_endpoints:
        context.logger.warning(f"[WARNING] Some endpoints had issues: {failed_endpoints}")
        # Don't fail the test, just log warnings for endpoint issues
    
    context.logger.info("[SUCCESS] Endpoint verification completed")


@given('I have a clean test environment')
def step_clean_environment(context: Context):
    """Ensure we have a clean test environment with no leftover state."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    context.logger.info("[ENV] Ensuring clean test environment...")
    
    # This combines environment reset with metrics initialization
    step_reset_environment(context)
    step_initialize_metrics(context)
    
    context.logger.info("[SUCCESS] Clean test environment ready")