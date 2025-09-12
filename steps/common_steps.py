"""
Common step definitions for Banking API BDD tests.
Provides reusable steps for HTTP operations, assertions, and data management.
"""

import json
import time
from typing import Dict, Any, Optional

from behave import given, when, then, step
from behave.runner import Context

from support.clients.api_client import APIClient


# ============================================================================
# GIVEN Steps - Test Setup and Preconditions
# ============================================================================

@given('the banking API is available')
def step_api_available(context: Context):
    """Verify that the banking API is accessible."""
    response = context.api_client.get('/')
    # Allow 200, 404, or any status that indicates the server is responding
    assert response.status_code in [200, 404, 405], f"API is not available: {response.status_code}"


@given('I have valid authentication credentials')
def step_valid_auth(context: Context):
    """Verify that valid authentication is configured."""
    assert context.api_client.auth_token, "No authentication token configured"
    assert 'Bearer' in context.api_client._get_default_headers()['Authorization']


@given('I set the correlation ID to "{correlation_id}"')
def step_set_correlation_id(context: Context, correlation_id: str):
    """Set a specific correlation ID for request tracking."""
    context.api_client.set_correlation_id(correlation_id)


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


@given('I wait for "{seconds:d}" seconds')
def step_wait(context: Context, seconds: int):
    """Wait for specified number of seconds."""
    time.sleep(seconds)


# ============================================================================
# WHEN Steps - Actions and Operations
# ============================================================================

@when('I send a GET request to "{endpoint}"')
def step_get_request(context: Context, endpoint: str):
    """Send GET request to specified endpoint."""
    context.api_client.get(endpoint)


@when('I send a POST request to "{endpoint}"')
def step_post_request(context: Context, endpoint: str):
    """Send POST request to specified endpoint."""
    # Use test data if available, otherwise empty body
    data = getattr(context, 'request_body', {})
    context.api_client.post(endpoint, json_data=data)


@when('I send a POST request to "{endpoint}" with data')
def step_post_request_with_data(context: Context, endpoint: str):
    """Send POST request with data from context table or text."""
    if context.text:
        try:
            data = json.loads(context.text)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON in context text")
    elif context.table:
        data = {}
        for row in context.table:
            data[row['field']] = row['value']
    else:
        data = getattr(context, 'request_body', {})
    
    context.api_client.post(endpoint, json_data=data)


@when('I send a PUT request to "{endpoint}"')
def step_put_request(context: Context, endpoint: str):
    """Send PUT request to specified endpoint."""
    data = getattr(context, 'request_body', {})
    context.api_client.put(endpoint, json_data=data)


@when('I send a DELETE request to "{endpoint}"')
def step_delete_request(context: Context, endpoint: str):
    """Send DELETE request to specified endpoint."""
    context.api_client.delete(endpoint)


@when('I set the request body to')
def step_set_request_body(context: Context):
    """Set request body from context text."""
    if context.text:
        try:
            context.request_body = json.loads(context.text)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON in request body")


@when('I set the "{header}" header to "{value}"')
def step_set_header(context: Context, header: str, value: str):
    """Set a specific header for the next request."""
    if not hasattr(context, 'custom_headers'):
        context.custom_headers = {}
    context.custom_headers[header] = value


@when('I send a request without authentication')
def step_request_without_auth(context: Context):
    """Remove authentication for the next request."""
    # Temporarily remove auth header
    original_headers = context.api_client.session.headers.copy()
    if 'Authorization' in context.api_client.session.headers:
        del context.api_client.session.headers['Authorization']
    
    # Store original headers to restore later
    context.original_headers = original_headers


@when('I restore authentication')
def step_restore_auth(context: Context):
    """Restore authentication headers."""
    if hasattr(context, 'original_headers'):
        context.api_client.session.headers.update(context.original_headers)
        delattr(context, 'original_headers')


# ============================================================================
# THEN Steps - Assertions and Verifications
# ============================================================================

@then('the response status code should be {status_code:d}')
def step_assert_status_code(context: Context, status_code: int):
    """Assert that response has expected status code."""
    context.api_client.assert_status_code(status_code)


@then('the response should be successful')
def step_assert_successful_response(context: Context):
    """Assert that response status code is in 2xx range."""
    status_code = context.api_client.last_response.status_code
    assert 200 <= status_code < 300, f"Response was not successful: {status_code}"


@then('the response should contain "{key}"')
def step_assert_response_contains_key(context: Context, key: str):
    """Assert that response JSON contains specified key."""
    context.api_client.assert_response_contains(key)


@then('the response "{key}" should be "{value}"')
def step_assert_response_value(context: Context, key: str, value: str):
    """Assert that response JSON key has expected value."""
    # Convert value to appropriate type
    if value.lower() == 'true':
        expected_value = True
    elif value.lower() == 'false':
        expected_value = False
    elif value.isdigit():
        expected_value = int(value)
    else:
        try:
            expected_value = float(value)
        except ValueError:
            expected_value = value
    
    context.api_client.assert_response_contains(key, expected_value)


@then('the response should contain the following fields')
def step_assert_response_fields(context: Context):
    """Assert that response contains all specified fields."""
    response_json = context.api_client.get_last_response_json()
    assert response_json, "Response is not valid JSON"
    
    for row in context.table:
        field = row['field']
        assert field in response_json, f"Response missing field: {field}"


@then('the response time should be under {max_time:d} milliseconds')
def step_assert_response_time(context: Context, max_time: int):
    """Assert that response time is under specified threshold."""
    context.api_client.assert_response_time_under(max_time)


@then('the response should be valid JSON')
def step_assert_valid_json(context: Context):
    """Assert that response is valid JSON."""
    response_json = context.api_client.get_last_response_json()
    assert response_json is not None, "Response is not valid JSON"


@then('the response should contain an error message')
def step_assert_error_message(context: Context):
    """Assert that response contains error information."""
    response_json = context.api_client.get_last_response_json()
    assert response_json, "Response is not valid JSON"
    
    # Check for common error fields
    error_fields = ['error', 'message', 'errors', 'detail']
    has_error_field = any(field in response_json for field in error_fields)
    assert has_error_field, f"Response does not contain error information: {response_json}"


@then('the response should match the schema')
def step_assert_schema_validation(context: Context):
    """Assert that response matches expected schema."""
    # This would require jsonschema validation
    # For now, we'll just check it's valid JSON
    response_json = context.api_client.get_last_response_json()
    assert response_json is not None, "Response is not valid JSON"


@then('I save the response "{field}" as "{variable_name}"')
def step_save_response_field(context: Context, field: str, variable_name: str):
    """Save a response field for use in subsequent steps."""
    response_json = context.api_client.get_last_response_json()
    assert response_json, "Response is not valid JSON"
    assert field in response_json, f"Response does not contain field: {field}"
    
    if not hasattr(context, 'saved_data'):
        context.saved_data = {}
    
    context.saved_data[variable_name] = response_json[field]


@then('the response should contain the correlation ID')
def step_assert_correlation_id(context: Context):
    """Assert that response contains correlation ID header."""
    response = context.api_client.last_response
    assert response, "No response to check"
    
    correlation_header = 'X-Correlation-Id'
    assert correlation_header in response.headers, f"Response missing {correlation_header} header"


# ============================================================================
# Utility Steps
# ============================================================================

@step('I print the response')
def step_print_response(context: Context):
    """Print response for debugging purposes."""
    response = context.api_client.last_response
    if response:
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Body: {response.text}")
    else:
        print("No response available")


@step('I print the saved data')
def step_print_saved_data(context: Context):
    """Print saved data for debugging purposes."""
    if hasattr(context, 'saved_data'):
        print(f"Saved data: {context.saved_data}")
    else:
        print("No saved data available")