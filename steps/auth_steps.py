"""
Authentication-specific step definitions for Banking API BDD tests.
Handles bearer token authentication, authorization scenarios, and security testing.
"""

import json
from behave import given, when, then
from behave.runner import Context


# ============================================================================
# GIVEN Steps - Authentication Setup
# ============================================================================

@given('I have a valid bearer token')
def step_valid_bearer_token(context: Context):
    """Verify that a valid bearer token is configured."""
    auth_header = context.api_client._get_default_headers().get('Authorization', '')
    assert auth_header.startswith('Bearer '), "Valid bearer token not configured"
    assert len(auth_header.split(' ')) == 2, "Invalid bearer token format"
    
    # Store the original token for restoration
    context.original_auth_token = context.api_client.auth_token


@given('I have an invalid bearer token')
def step_invalid_bearer_token(context: Context):
    """Set an invalid bearer token for testing."""
    # Store original token for restoration
    context.original_auth_token = context.api_client.auth_token
    
    # Set invalid token
    context.api_client.auth_token = 'invalid-token-12345'
    context.api_client.reset_session()


@given('I have an expired bearer token')
def step_expired_bearer_token(context: Context):
    """Set an expired bearer token for testing."""
    # Store original token for restoration
    context.original_auth_token = context.api_client.auth_token
    
    # Set expired token (this would be a real expired token in practice)
    context.api_client.auth_token = 'expired-banking-api-key-2023'
    context.api_client.reset_session()


@given('I have no authentication token')
def step_no_auth_token(context: Context):
    """Remove authentication token for testing."""
    # Store original token for restoration
    context.original_auth_token = context.api_client.auth_token
    
    # Remove auth token
    context.api_client.auth_token = ''
    context.api_client.reset_session()


@given('I use the correct banking API key')
def step_correct_api_key(context: Context):
    """Ensure we're using the correct banking API key."""
    context.api_client.auth_token = 'banking-api-key-2024'
    context.api_client.reset_session()


# ============================================================================
# WHEN Steps - Authentication Actions
# ============================================================================

@when('I authenticate with bearer token "{token}"')
def step_authenticate_with_token(context: Context, token: str):
    """Authenticate using a specific bearer token."""
    # Store original token for restoration
    if not hasattr(context, 'original_auth_token'):
        context.original_auth_token = context.api_client.auth_token
    
    context.api_client.auth_token = token
    context.api_client.reset_session()


@when('I remove the Authorization header')
def step_remove_auth_header(context: Context):
    """Remove the Authorization header from requests."""
    if 'Authorization' in context.api_client.session.headers:
        # Store for restoration
        context.removed_auth_header = context.api_client.session.headers['Authorization']
        del context.api_client.session.headers['Authorization']


@when('I restore the Authorization header')
def step_restore_auth_header(context: Context):
    """Restore the Authorization header."""
    if hasattr(context, 'removed_auth_header'):
        context.api_client.session.headers['Authorization'] = context.removed_auth_header
        delattr(context, 'removed_auth_header')


@when('I send a request with malformed Authorization header')
def step_malformed_auth_header(context: Context):
    """Send request with malformed Authorization header."""
    # Store original header
    context.original_auth_header = context.api_client.session.headers.get('Authorization')
    
    # Set malformed header (missing 'Bearer' prefix)
    context.api_client.session.headers['Authorization'] = context.api_client.auth_token


@when('I send a request with empty Authorization header')
def step_empty_auth_header(context: Context):
    """Send request with empty Authorization header."""
    # Store original header
    context.original_auth_header = context.api_client.session.headers.get('Authorization')
    
    # Set empty header
    context.api_client.session.headers['Authorization'] = ''


@when('I send concurrent requests with the same token')
def step_concurrent_requests_same_token(context: Context):
    """Send multiple concurrent requests with the same authentication token."""
    import concurrent.futures
    import threading
    
    results = []
    
    def make_request():
        """Make API request in thread."""
        try:
            response = context.api_client.get('/customers/CUST001')
            return {
                'status_code': response.status_code,
                'thread_id': threading.current_thread().ident,
                'response_time': context.api_client.last_response_time
            }
        except Exception as e:
            return {'error': str(e), 'thread_id': threading.current_thread().ident}
    
    # Execute 5 concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_request) for _ in range(5)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    # Store results for verification
    context.concurrent_results = results


# ============================================================================
# THEN Steps - Authentication Assertions
# ============================================================================

@then('I should receive an unauthorized error')
def step_assert_unauthorized(context: Context):
    """Assert that the response indicates unauthorized access."""
    response = context.api_client.last_response
    assert response.status_code == 401, f"Expected 401 Unauthorized, got {response.status_code}"
    
    # Check for WWW-Authenticate header
    assert 'WWW-Authenticate' in response.headers, "Missing WWW-Authenticate header"
    
    # Verify error response structure
    response_json = context.api_client.get_last_response_json()
    if response_json:
        assert 'error' in response_json or 'code' in response_json, "Response should contain error information"


@then('I should receive a forbidden error')
def step_assert_forbidden(context: Context):
    """Assert that the response indicates forbidden access."""
    response = context.api_client.last_response
    assert response.status_code == 403, f"Expected 403 Forbidden, got {response.status_code}"
    
    # Verify error response structure
    response_json = context.api_client.get_last_response_json()
    if response_json:
        assert 'error' in response_json, "Response should contain error information"


@then('the error message should indicate missing authorization')
def step_assert_missing_auth_message(context: Context):
    """Assert that error message indicates missing authorization."""
    response_json = context.api_client.get_last_response_json()
    assert response_json, "Response should be valid JSON"
    
    # Check for specific error code/message
    error_indicators = [
        'MISSING_AUTHORIZATION',
        'Authorization header is required',
        'missing authorization',
        'unauthorized'
    ]
    
    response_text = json.dumps(response_json).lower()
    has_auth_error = any(indicator.lower() in response_text for indicator in error_indicators)
    assert has_auth_error, f"Response should indicate missing authorization: {response_json}"


@then('the error message should indicate invalid token')
def step_assert_invalid_token_message(context: Context):
    """Assert that error message indicates invalid token."""
    response_json = context.api_client.get_last_response_json()
    assert response_json, "Response should be valid JSON"
    
    # Check for specific error code/message
    error_indicators = [
        'INVALID_TOKEN',
        'invalid token',
        'token is invalid',
        'authentication failed'
    ]
    
    response_text = json.dumps(response_json).lower()
    has_token_error = any(indicator.lower() in response_text for indicator in error_indicators)
    assert has_token_error, f"Response should indicate invalid token: {response_json}"


@then('all concurrent requests should succeed')
def step_assert_concurrent_success(context: Context):
    """Assert that all concurrent requests were successful."""
    assert hasattr(context, 'concurrent_results'), "No concurrent request results found"
    
    for result in context.concurrent_results:
        assert 'error' not in result, f"Request failed with error: {result.get('error')}"
        assert result.get('status_code') == 200, f"Expected 200, got {result.get('status_code')}"


@then('all concurrent requests should be unauthorized')
def step_assert_concurrent_unauthorized(context: Context):
    """Assert that all concurrent requests were unauthorized."""
    assert hasattr(context, 'concurrent_results'), "No concurrent request results found"
    
    for result in context.concurrent_results:
        if 'status_code' in result:
            assert result['status_code'] == 401, f"Expected 401, got {result.get('status_code')}"


@then('the WWW-Authenticate header should be present')
def step_assert_www_authenticate_header(context: Context):
    """Assert that WWW-Authenticate header is present in the response."""
    response = context.api_client.last_response
    assert response, "No response available"
    
    auth_header = response.headers.get('WWW-Authenticate')
    assert auth_header, "WWW-Authenticate header is missing"
    assert 'Bearer' in auth_header, "WWW-Authenticate header should indicate Bearer token requirement"


@then('I restore the original authentication')
def step_restore_original_auth(context: Context):
    """Restore the original authentication token."""
    if hasattr(context, 'original_auth_token'):
        context.api_client.auth_token = context.original_auth_token
        context.api_client.reset_session()
        delattr(context, 'original_auth_token')
    
    if hasattr(context, 'original_auth_header'):
        context.api_client.session.headers['Authorization'] = context.original_auth_header
        delattr(context, 'original_auth_header')


@then('the response should include security headers')
def step_assert_security_headers(context: Context):
    """Assert that response includes appropriate security headers."""
    response = context.api_client.last_response
    assert response, "No response available"
    
    # Check for common security headers
    security_headers = {
        'X-Correlation-Id': 'Request tracking header',
        'Content-Type': 'Content type specification'
    }
    
    for header, description in security_headers.items():
        assert header in response.headers, f"Missing security header: {header} ({description})"


@then('the authentication should be case-sensitive')
def step_assert_case_sensitive_auth(context: Context):
    """Verify that authentication is case-sensitive by testing different cases."""
    original_token = context.api_client.auth_token
    
    # Test with different case
    case_variants = [
        original_token.upper(),
        original_token.lower(),
        original_token.capitalize()
    ]
    
    for variant in case_variants:
        if variant != original_token:
            context.api_client.auth_token = variant
            context.api_client.reset_session()
            
            # Try to make a request
            response = context.api_client.get('/customers/CUST001')
            
            # Should fail with different case (unless original was already in that case)
            assert response.status_code in [401, 403], f"Authentication should be case-sensitive, but {variant} worked"
    
    # Restore original token
    context.api_client.auth_token = original_token
    context.api_client.reset_session()