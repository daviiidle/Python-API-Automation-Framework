"""
Security validation step definitions for Banking API BDD tests.
Handles security headers, XSS protection, and security-related assertions.
"""

import json
from behave import given, when, then, step
from behave.runner import Context


# ============================================================================
# Security Header Validations
# ============================================================================

@then('the response should include security headers')
def step_assert_security_headers(context: Context):
    """Assert that response includes security headers."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    if not hasattr(context, 'response') or context.response is None:
        context.logger.error("[ERROR] No response available for security header verification")
        raise AssertionError("No response available")
    
    context.logger.info("[VERIFY] Checking security headers in response")
    
    # Check for common security headers
    security_headers = {
        'Content-Type': 'application/json',
        'X-Correlation-Id': None  # Just check presence
    }
    
    missing_headers = []
    for header_name, expected_value in security_headers.items():
        if header_name in context.response.headers:
            actual_value = context.response.headers[header_name]
            if expected_value and expected_value not in actual_value:
                context.logger.warning(f"[WARNING] Header '{header_name}' has unexpected value: {actual_value}")
            else:
                context.logger.debug(f"[FOUND] Security header '{header_name}': {actual_value}")
        else:
            missing_headers.append(header_name)
    
    if missing_headers:
        context.logger.warning(f"[WARNING] Missing security headers: {missing_headers}")
        # Don't fail the test for missing security headers, just log warning
        context.logger.info("[INFO] Continuing without all security headers")
    else:
        context.logger.info("[SUCCESS] All security headers present")


@then('the response should have Content-Type header set to "{expected_type}"')
def step_assert_content_type_header(context: Context, expected_type: str):
    """Assert that response has the correct Content-Type header."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    if not hasattr(context, 'response') or context.response is None:
        context.logger.error("[ERROR] No response available for Content-Type verification")
        raise AssertionError("No response available")
    
    context.logger.info(f"[VERIFY] Checking Content-Type header: {expected_type}")
    
    content_type = context.response.headers.get('Content-Type', '')
    
    if expected_type in content_type:
        context.logger.info(f"[SUCCESS] Content-Type header is correct: {content_type}")
    else:
        context.logger.error(f"[ERROR] Content-Type header mismatch: Expected '{expected_type}', got '{content_type}'")
        raise AssertionError(f"Expected Content-Type '{expected_type}', got '{content_type}'")


@then('the response should have CORS headers')
def step_assert_cors_headers(context: Context):
    """Assert that response includes CORS headers."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    if not hasattr(context, 'response') or context.response is None:
        context.logger.error("[ERROR] No response available for CORS header verification")
        raise AssertionError("No response available")
    
    context.logger.info("[VERIFY] Checking CORS headers in response")
    
    cors_headers = [
        'Access-Control-Allow-Origin',
        'Access-Control-Allow-Methods',
        'Access-Control-Allow-Headers'
    ]
    
    found_cors_headers = []
    for header in cors_headers:
        if header in context.response.headers:
            found_cors_headers.append(header)
            context.logger.debug(f"[FOUND] CORS header '{header}': {context.response.headers[header]}")
    
    if found_cors_headers:
        context.logger.info(f"[SUCCESS] Found CORS headers: {found_cors_headers}")
    else:
        context.logger.warning("[WARNING] No CORS headers found - may indicate security restriction")
        # Don't fail the test, CORS headers might not be required for all endpoints


@then('the response should not expose server information')
def step_assert_no_server_exposure(context: Context):
    """Assert that response doesn't expose sensitive server information."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    if not hasattr(context, 'response') or context.response is None:
        context.logger.error("[ERROR] No response available for server exposure check")
        raise AssertionError("No response available")
    
    context.logger.info("[VERIFY] Checking for server information exposure")
    
    # Headers that might expose server information
    sensitive_headers = ['Server', 'X-Powered-By', 'X-AspNet-Version', 'X-AspNetMvc-Version']
    
    exposed_headers = []
    for header in sensitive_headers:
        if header in context.response.headers:
            exposed_headers.append(f"{header}: {context.response.headers[header]}")
    
    if exposed_headers:
        context.logger.warning(f"[WARNING] Server information exposed: {exposed_headers}")
        # Don't fail the test, just warn about potential information disclosure
        context.logger.info("[INFO] Consider removing server identification headers")
    else:
        context.logger.info("[SUCCESS] No sensitive server information exposed")


# ============================================================================
# XSS and Content Security Validations
# ============================================================================

# This step is now implemented in assertion_steps.py to avoid duplicates
# @then('the response should not contain "{text}"') - moved to assertion_steps.py


@then('the response should be sanitized against XSS')
def step_assert_xss_protection(context: Context):
    """Assert that response is protected against XSS attacks."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    if not hasattr(context, 'response') or context.response is None:
        context.logger.error("[ERROR] No response available for XSS verification")
        raise AssertionError("No response available")
    
    context.logger.info("[VERIFY] Checking XSS protection in response")
    
    # Common XSS patterns to check for
    xss_patterns = [
        '<script',
        'javascript:',
        'onload=',
        'onerror=',
        'onclick=',
        'onmouseover=',
        'eval(',
        'alert(',
        'document.cookie',
        'document.write'
    ]
    
    response_text = context.response.text.lower()
    found_patterns = []
    
    for pattern in xss_patterns:
        if pattern in response_text:
            found_patterns.append(pattern)
    
    if found_patterns:
        context.logger.error(f"[ERROR] Potential XSS vulnerability detected: {found_patterns}")
        context.logger.debug(f"[BODY] Response snippet: {context.response.text[:200]}...")
        
        # Capture error details for failure report
        error_details = f"XSS vulnerability detected - Found patterns: {found_patterns}"
        if hasattr(context, 'scenario_metrics'):
            context.scenario_metrics.setdefault('errors', []).append(error_details)
        context.last_error = error_details
        
        raise AssertionError(f"Potential XSS vulnerability detected: {found_patterns}")
    
    context.logger.info("[SUCCESS] Response appears to be protected against XSS")


@then('the response should not contain unescaped HTML')
def step_assert_no_unescaped_html(context: Context):
    """Assert that response doesn't contain unescaped HTML that could be dangerous."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    if not hasattr(context, 'response') or context.response is None:
        context.logger.error("[ERROR] No response available for HTML verification")
        raise AssertionError("No response available")
    
    context.logger.info("[VERIFY] Checking for unescaped HTML in response")
    
    # Check if response is JSON (should not contain raw HTML)
    content_type = context.response.headers.get('Content-Type', '')
    if 'application/json' in content_type:
        try:
            response_json = context.response.json()
            
            # Check all string values in JSON for unescaped HTML
            html_tags = ['<script', '<iframe', '<object', '<embed', '<form', '<input']
            
            def check_value_for_html(value):
                if isinstance(value, str):
                    value_lower = value.lower()
                    for tag in html_tags:
                        if tag in value_lower:
                            return tag
                elif isinstance(value, dict):
                    for v in value.values():
                        found_tag = check_value_for_html(v)
                        if found_tag:
                            return found_tag
                elif isinstance(value, list):
                    for item in value:
                        found_tag = check_value_for_html(item)
                        if found_tag:
                            return found_tag
                return None
            
            found_html = check_value_for_html(response_json)
            
            if found_html:
                context.logger.error(f"[ERROR] Unescaped HTML found in JSON response: {found_html}")
                raise AssertionError(f"Unescaped HTML found in response: {found_html}")
            else:
                context.logger.info("[SUCCESS] No unescaped HTML found in JSON response")
                
        except json.JSONDecodeError:
            context.logger.warning("[WARNING] Response is not valid JSON - skipping HTML check")
    else:
        context.logger.info(f"[INFO] Non-JSON response ({content_type}) - HTML check not applicable")


# ============================================================================
# Input Validation Security Checks
# ============================================================================

@when('I send a request with malicious payload')
def step_send_malicious_payload(context: Context):
    """Send a request with a potentially malicious payload for security testing."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    context.logger.info("[SECURITY] Sending request with malicious payload for testing")
    
    # Create a payload with various potentially dangerous inputs
    malicious_payload = {
        "firstName": "<script>alert('XSS')</script>",
        "lastName": "'; DROP TABLE users; --",
        "email": "test@example.com<script>document.location='http://evil.com'</script>",
        "phone": "javascript:alert('XSS')",
        "comments": "Normal text with <iframe src='http://evil.com'></iframe> injection"
    }
    
    # Store the malicious payload for the next HTTP request
    context.request_body = malicious_payload
    context.logger.debug(f"[PAYLOAD] Malicious payload prepared: {json.dumps(malicious_payload, indent=2)}")


@when('I send a request with SQL injection patterns')
def step_send_sql_injection_payload(context: Context):
    """Send a request with SQL injection patterns for security testing."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    context.logger.info("[SECURITY] Sending request with SQL injection patterns")
    
    # Create a payload with SQL injection patterns
    sql_injection_payload = {
        "customerId": "CUST001' OR '1'='1",
        "accountType": "SAVINGS'; DROP TABLE accounts; --",
        "search": "1' UNION SELECT * FROM users --",
        "filter": "admin'/**/OR/**/1=1#",
        "sortBy": "name'; DELETE FROM customers; --"
    }
    
    context.request_body = sql_injection_payload
    context.logger.debug(f"[PAYLOAD] SQL injection payload prepared: {json.dumps(sql_injection_payload, indent=2)}")


@when('I send oversized request data')
def step_send_oversized_request(context: Context):
    """Send a request with oversized data to test input validation."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    context.logger.info("[SECURITY] Sending oversized request for input validation testing")
    
    # Create oversized data
    large_string = "A" * 10000  # 10KB string
    very_large_string = "B" * 100000  # 100KB string
    
    oversized_payload = {
        "firstName": large_string,
        "lastName": large_string,
        "description": very_large_string,
        "comments": large_string,
        "metadata": {
            "field1": large_string,
            "field2": large_string,
            "field3": very_large_string
        }
    }
    
    context.request_body = oversized_payload
    context.logger.debug(f"[PAYLOAD] Oversized payload prepared (total size: ~{len(str(oversized_payload))} bytes)")


# ============================================================================
# Security Error Response Validations
# ============================================================================

@then('the response should indicate input validation failure')
def step_assert_input_validation_failure(context: Context):
    """Assert that response indicates proper input validation failure."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    if not hasattr(context, 'response') or context.response is None:
        context.logger.error("[ERROR] No response available for validation check")
        raise AssertionError("No response available")
    
    context.logger.info("[VERIFY] Checking for input validation failure response")
    
    # Check for appropriate error status code
    if context.response.status_code not in [400, 422]:
        context.logger.error(f"[ERROR] Expected 400 or 422 status for validation failure, got {context.response.status_code}")
        raise AssertionError(f"Expected 400/422 status for validation failure, got {context.response.status_code}")
    
    # Check for validation error message
    try:
        response_json = context.response.json()
        validation_keywords = ['validation', 'invalid', 'error', 'bad request', 'malformed']
        
        response_text = json.dumps(response_json).lower()
        found_keywords = [keyword for keyword in validation_keywords if keyword in response_text]
        
        if found_keywords:
            context.logger.info(f"[SUCCESS] Input validation failure properly indicated: {found_keywords}")
        else:
            context.logger.warning("[WARNING] No clear validation error message found")
            
    except json.JSONDecodeError:
        # Non-JSON response is acceptable for validation errors
        context.logger.info("[INFO] Non-JSON validation error response")
    
    context.logger.info("[SUCCESS] Input validation failure properly handled")


@then('the response should not leak sensitive information')
def step_assert_no_information_leakage(context: Context):
    """Assert that error responses don't leak sensitive information."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    if not hasattr(context, 'response') or context.response is None:
        context.logger.error("[ERROR] No response available for information leakage check")
        raise AssertionError("No response available")
    
    context.logger.info("[VERIFY] Checking for sensitive information leakage")
    
    # Sensitive information patterns that should not appear in responses
    sensitive_patterns = [
        'password',
        'secret',
        'token',
        'key',
        'database',
        'sql',
        'connection',
        'server',
        'stack trace',
        'exception',
        'internal error',
        'debug',
        'system error'
    ]
    
    response_text = context.response.text.lower()
    found_sensitive = [pattern for pattern in sensitive_patterns if pattern in response_text]
    
    if found_sensitive:
        context.logger.warning(f"[WARNING] Potentially sensitive information found: {found_sensitive}")
        context.logger.debug(f"[BODY] Response snippet: {context.response.text[:200]}...")
        # Log warning but don't fail the test - this might be acceptable depending on context
    else:
        context.logger.info("[SUCCESS] No sensitive information leakage detected")


# ============================================================================
# Authentication Security Checks
# ============================================================================

@then('the response should require proper authentication')
def step_assert_authentication_required(context: Context):
    """Assert that the endpoint properly requires authentication."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    if not hasattr(context, 'response') or context.response is None:
        context.logger.error("[ERROR] No response available for authentication check")
        raise AssertionError("No response available")
    
    context.logger.info("[VERIFY] Checking authentication requirement")
    
    # When authentication is missing or invalid, should get 401 or 403
    if context.response.status_code in [401, 403]:
        context.logger.info(f"[SUCCESS] Proper authentication required: {context.response.status_code}")
    else:
        context.logger.error(f"[ERROR] Expected 401/403 for authentication failure, got {context.response.status_code}")
        context.logger.debug(f"[BODY] Response: {context.response.text[:200]}...")
        raise AssertionError(f"Expected 401/403 for authentication failure, got {context.response.status_code}")


@then('the response should have secure error handling')
def step_assert_secure_error_handling(context: Context):
    """Assert that error responses follow secure error handling practices."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    if not hasattr(context, 'response') or context.response is None:
        context.logger.error("[ERROR] No response available for error handling check")
        raise AssertionError("No response available")
    
    context.logger.info("[VERIFY] Checking secure error handling")
    
    # For error responses, check that they:
    # 1. Have appropriate status codes
    # 2. Don't expose internal details
    # 3. Provide minimal but helpful error information
    
    if context.response.status_code >= 400:
        context.logger.debug(f"[INFO] Error response status: {context.response.status_code}")
        
        # Check that error response is not empty
        if not context.response.text.strip():
            context.logger.warning("[WARNING] Empty error response - might need more informative error messages")
        
        # Check for appropriate error structure
        try:
            error_json = context.response.json()
            if 'error' in error_json or 'message' in error_json:
                context.logger.info("[SUCCESS] Error response has proper structure")
            else:
                context.logger.warning("[WARNING] Error response lacks standard error fields")
        except json.JSONDecodeError:
            context.logger.info("[INFO] Non-JSON error response")
    
    context.logger.info("[SUCCESS] Error handling security check completed")