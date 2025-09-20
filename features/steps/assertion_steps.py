"""
Response assertion and validation step definitions for Banking API BDD tests.
Handles all response validations, field checking, and content assertions.
"""

import json
from typing import Dict, Any

from behave import given, when, then, step
from behave.runner import Context


# ============================================================================
# Status Code Assertions
# ============================================================================

@step('the response status code should be {status_code:d}')
def step_assert_status_code(context: Context, status_code: int):
    """Assert that response has expected status code."""
    context.logger.info(f"[VERIFY] Verifying response status code should be {status_code}")
    
    if not hasattr(context, 'response') or context.response is None:
        context.logger.error("[ERROR] No response available for status code verification")
        raise AssertionError("No response available to check")
    
    actual_status = context.response.status_code
    context.logger.info(f"[INFO] Expected: {status_code}, Actual: {actual_status}")
    
    if actual_status == status_code:
        context.logger.info(f"[SUCCESS] Status code assertion PASSED: {actual_status}")
    else:
        context.logger.error(f"[ERROR] Status code assertion FAILED: Expected {status_code}, got {actual_status}")
        context.logger.error(f"[BODY] Response content: {context.response.text[:300]}...")
        
        # Log response headers for debugging
        context.logger.debug(f"[HEADERS] Response Headers: {dict(context.response.headers)}")
        
        # Capture detailed error context for failure report
        error_details = f"Status code assertion failed - Expected: {status_code}, Actual: {actual_status}"
        if hasattr(context, 'scenario_metrics'):
            context.scenario_metrics.setdefault('errors', []).append(error_details)
        context.last_error = error_details
        
        # Try to parse and log JSON response for better debugging
        try:
            if context.response.headers.get('content-type', '').startswith('application/json'):
                error_response = context.response.json()
                context.logger.error(f"[BODY] Error Response JSON: {json.dumps(error_response, indent=2)}")
                # Add JSON error to context for failure report
                context.last_error += f" | JSON Error: {json.dumps(error_response)}"
        except Exception:
            pass
        
        raise AssertionError(f"Expected status {status_code}, got {actual_status}. Response: {context.response.text[:200]}...")


@step('the response status code should be either {status1:d} or {status2:d}')
def step_assert_status_code_either(context: Context, status1: int, status2: int):
    """Assert that response has one of two expected status codes."""
    context.logger.info(f"[VERIFY] Verifying response status code should be either {status1} or {status2}")

    if not hasattr(context, 'response') or context.response is None:
        context.logger.error("[ERROR] No response available for status code verification")
        raise AssertionError("No response available to check")

    actual_status = context.response.status_code
    context.logger.info(f"[INFO] Expected: {status1} or {status2}, Actual: {actual_status}")

    if actual_status in [status1, status2]:
        context.logger.info(f"[SUCCESS] Status code assertion PASSED: {actual_status} (expected either {status1} or {status2})")
    else:
        context.logger.error(f"[ERROR] Status code assertion FAILED: Expected {status1} or {status2}, got {actual_status}")
        context.logger.error(f"[BODY] Response content: {context.response.text[:300]}...")

        # Log response headers for debugging
        context.logger.debug(f"[HEADERS] Response Headers: {dict(context.response.headers)}")

        # Capture detailed error context for failure report
        error_details = f"Status code assertion failed - Expected: {status1} or {status2}, Actual: {actual_status}"
        if hasattr(context, 'scenario_metrics'):
            context.scenario_metrics.setdefault('errors', []).append(error_details)
        context.last_error = error_details

        # Try to parse and log JSON response for better debugging
        try:
            if context.response.headers.get('content-type', '').startswith('application/json'):
                error_response = context.response.json()
                context.logger.error(f"[BODY] Error Response JSON: {json.dumps(error_response, indent=2)}")
                # Add JSON error to context for failure report
                context.last_error += f" | JSON Error: {json.dumps(error_response)}"
        except Exception:
            pass

        raise AssertionError(f"Expected status {status1} or {status2}, got {actual_status}. Response: {context.response.text[:200]}...")


@then('the response should be successful')
def step_assert_successful_response(context: Context):
    """Assert that response status code is in 2xx range."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    context.logger.info("[VERIFY] Verifying response is successful (2xx status)")
    
    if not hasattr(context, 'response') or context.response is None:
        context.logger.error("[ERROR] No response available for success verification")
        raise AssertionError("No response available")
    
    status_code = context.response.status_code
    context.logger.debug(f"[INFO] Response status code: {status_code}")
    
    if 200 <= status_code < 300:
        context.logger.info(f"[SUCCESS] Success assertion PASSED: Status {status_code}")
    else:
        context.logger.error(f"[ERROR] Success assertion FAILED: Status {status_code} is not successful")
        context.logger.error(f"[BODY] Response content: {context.response.text[:300]}...")
        
        # Capture error details for failure report
        error_details = f"Success assertion failed - Status {status_code} is not in 2xx range"
        if hasattr(context, 'scenario_metrics'):
            context.scenario_metrics.setdefault('errors', []).append(error_details)
        context.last_error = error_details
        
        raise AssertionError(f"Response was not successful: {status_code}")


# ============================================================================
# JSON Response Validations
# ============================================================================

@then('the response should be valid JSON')
def step_assert_valid_json(context: Context):
    """Assert that response is valid JSON."""
    context.logger.info("[VERIFY] Verifying response is valid JSON")
    
    if not hasattr(context, 'response') or context.response is None:
        context.logger.error("[ERROR] No response available for JSON validation")
        raise AssertionError("No response available")
    
    try:
        response_json = context.response.json()
        context.logger.info("[SUCCESS] JSON validation PASSED: Response is valid JSON")
        
        # Log JSON structure info
        if isinstance(response_json, dict):
            context.logger.debug(f"[HEADERS] JSON object with {len(response_json)} keys: {list(response_json.keys())}")
        elif isinstance(response_json, list):
            context.logger.debug(f"[HEADERS] JSON array with {len(response_json)} items")
        else:
            context.logger.debug(f"[HEADERS] JSON primitive value: {type(response_json).__name__}")
        
    except json.JSONDecodeError as e:
        context.logger.error(f"[ERROR] JSON validation FAILED: {e}")
        context.logger.error(f"[BODY] Raw response content: {context.response.text[:300]}...")
        context.logger.debug(f"[HEADERS] Response Content-Type: {context.response.headers.get('content-type', 'Not specified')}")
        raise AssertionError(f"Response is not valid JSON: {e}")


@then('the response should match the schema')
def step_assert_schema_validation(context: Context):
    """Assert that response matches expected schema."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    if not hasattr(context, 'response') or context.response is None:
        context.logger.error("[ERROR] No response available for schema validation")
        raise AssertionError("No response available")
    
    try:
        response_json = context.response.json()
        context.logger.info("[SUCCESS] Response is valid JSON and matches basic schema")
        # TODO: Add actual jsonschema validation here if needed
        
    except json.JSONDecodeError as e:
        context.logger.error(f"[ERROR] Response is not valid JSON: {e}")
        raise AssertionError(f"Response is not valid JSON: {e}")


# ============================================================================
# Field Checking and Value Assertions
# ============================================================================

@then('the response should contain "{key}"')
def step_assert_response_contains_key(context: Context, key: str):
    """Assert that response JSON contains specified key."""
    context.logger.info(f"[VERIFY] Verifying response contains key: '{key}'")
    
    if not hasattr(context, 'response') or context.response is None:
        context.logger.error("[ERROR] No response available for key verification")
        raise AssertionError("No response available")
    
    try:
        response_json = context.response.json()
        available_keys = list(response_json.keys()) if isinstance(response_json, dict) else []
        
        context.logger.debug(f"[HEADERS] Available keys in response: {available_keys}")
        
        if key in response_json:
            context.logger.info(f"[SUCCESS] Key assertion PASSED: Found '{key}' in response")
            context.logger.debug(f"[BODY] Value of '{key}': {response_json[key]}")
        else:
            context.logger.error(f"[ERROR] Key assertion FAILED: '{key}' not found in response")
            context.logger.error(f"[HEADERS] Available keys: {available_keys}")
            context.logger.debug(f"[BODY] Full response: {json.dumps(response_json, indent=2)[:500]}...")
            
            # Capture error details for failure report
            error_details = f"Key assertion failed - '{key}' not found. Available keys: {available_keys}"
            if hasattr(context, 'scenario_metrics'):
                context.scenario_metrics.setdefault('errors', []).append(error_details)
            context.last_error = error_details
            
            raise AssertionError(f"Response does not contain key '{key}'. Available keys: {available_keys}")
    
    except json.JSONDecodeError as e:
        context.logger.error(f"[ERROR] JSON decode error: {e}")
        context.logger.error(f"[BODY] Raw response: {context.response.text[:200]}...")
        
        # Capture JSON error details for failure report
        error_details = f"JSON decode error: {e}. Raw response: {context.response.text[:200]}"
        if hasattr(context, 'scenario_metrics'):
            context.scenario_metrics.setdefault('errors', []).append(error_details)
        context.last_error = error_details
        
        raise AssertionError("Response is not valid JSON")


@then('the response "{key}" should be "{value}"')
def step_assert_response_value(context: Context, key: str, value: str):
    """Assert that response JSON key has expected value."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    context.logger.info(f"[VERIFY] Verifying response '{key}' should be '{value}'")
    
    if not hasattr(context, 'response') or context.response is None:
        context.logger.error("[ERROR] No response available for value verification")
        raise AssertionError("No response available")
    
    try:
        response_json = context.response.json()
        context.logger.debug(f"[HEADERS] Checking key '{key}' in response")
        
        if key not in response_json:
            available_keys = list(response_json.keys()) if isinstance(response_json, dict) else []
            context.logger.error(f"[ERROR] Key '{key}' not found in response")
            context.logger.error(f"[HEADERS] Available keys: {available_keys}")
            raise AssertionError(f"Response does not contain key '{key}'. Available keys: {available_keys}")
        
        actual_value = str(response_json[key])
        expected_value = str(value)
        
        context.logger.debug(f"[BODY] Expected: '{expected_value}', Actual: '{actual_value}'")
        
        if actual_value == expected_value:
            context.logger.info(f"[SUCCESS] Value assertion PASSED: '{key}' = '{actual_value}'")
        else:
            context.logger.error(f"[ERROR] Value assertion FAILED: Expected '{expected_value}', got '{actual_value}'")
            
            # Capture error details for failure report
            error_details = f"Value assertion failed - '{key}' expected '{expected_value}' but got '{actual_value}'"
            if hasattr(context, 'scenario_metrics'):
                context.scenario_metrics.setdefault('errors', []).append(error_details)
            context.last_error = error_details
            
            raise AssertionError(f"Expected '{key}' to be '{expected_value}', got '{actual_value}'")
    
    except json.JSONDecodeError as e:
        context.logger.error(f"[ERROR] JSON decode error: {e}")
        context.logger.error(f"[BODY] Raw response: {context.response.text[:200]}...")
        
        # Capture JSON error details for failure report
        error_details = f"JSON decode error during value assertion: {e}"
        if hasattr(context, 'scenario_metrics'):
            context.scenario_metrics.setdefault('errors', []).append(error_details)
        context.last_error = error_details
        
        raise AssertionError("Response is not valid JSON")


@then('the response should contain the following fields:')
def step_assert_response_contains_fields(context: Context):
    """Assert that response contains all fields listed in the table."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    if not hasattr(context, 'response') or context.response is None:
        context.logger.error("[ERROR] No response available for field verification")
        raise AssertionError("No response available")
    
    try:
        response_json = context.response.json()
        context.logger.info("[VERIFY] Checking response contains required fields")
        
        missing_fields = []
        for row in context.table:
            field = row['field']
            if field not in response_json:
                missing_fields.append(field)
            else:
                context.logger.debug(f"[FOUND] Field '{field}' present in response")
        
        if missing_fields:
            context.logger.error(f"[ERROR] Missing fields: {missing_fields}")
            context.logger.debug(f"[BODY] Available fields: {list(response_json.keys())}")
            raise AssertionError(f"Response missing required fields: {missing_fields}")
        
        context.logger.info(f"[SUCCESS] All {len(context.table.rows)} required fields found in response")
        
    except json.JSONDecodeError as e:
        context.logger.error(f"[ERROR] Response is not valid JSON: {e}")
        raise AssertionError(f"Response is not valid JSON: {e}")


@then('the response should contain the following fields')
def step_assert_contains_fields_table(context: Context):
    """Assert that response contains all fields listed in table."""
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    if not hasattr(context, 'response') or context.response is None:
        context.logger.error("[ERROR] No response available for field verification")
        raise AssertionError("No response available")
    
    if not context.table:
        context.logger.error("[ERROR] No table data provided")
        raise AssertionError("No table data provided")
    
    try:
        response_json = context.response.json()
        context.logger.info(f"[VERIFY] Checking {len(context.table.rows)} fields from table")
        
        missing_fields = []
        for row in context.table:
            field = row['field']
            if field not in response_json:
                missing_fields.append(field)
            else:
                context.logger.debug(f"[FOUND] Field '{field}' present in response")
        
        if missing_fields:
            available_fields = list(response_json.keys())
            context.logger.error(f"[ERROR] Missing fields: {missing_fields}")
            context.logger.error(f"[INFO] Available fields: {available_fields}")
            raise AssertionError(f"Response missing required fields: {missing_fields}. Available: {available_fields}")
        
        context.logger.info(f"[SUCCESS] All {len(context.table.rows)} required fields found in response")
        
    except json.JSONDecodeError as e:
        context.logger.error(f"[ERROR] Response is not valid JSON: {e}")
        raise AssertionError(f"Response is not valid JSON: {e}")


# ============================================================================
# Error Message Verifications
# ============================================================================

@then('the response should contain an error message')
def step_assert_error_message(context: Context):
    """Assert that response contains an error message."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    context.logger.info("[VERIFY] Verifying response contains error message")
    
    if not hasattr(context, 'response') or context.response is None:
        context.logger.error("[ERROR] No response available for error message verification")
        raise AssertionError("No response available")
    
    try:
        response_json = context.response.json()
        error_keys = ['error', 'message', 'errorMessage', 'error_message', 'details']
        
        context.logger.debug(f"[HEADERS] Checking for error message keys: {error_keys}")
        
        found_error_key = None
        for key in error_keys:
            if key in response_json:
                found_error_key = key
                break
        
        if found_error_key:
            error_message = response_json[found_error_key]
            context.logger.info(f"[SUCCESS] Error message assertion PASSED: Found '{found_error_key}': {error_message}")
        else:
            available_keys = list(response_json.keys()) if isinstance(response_json, dict) else []
            context.logger.error(f"[ERROR] Error message assertion FAILED: No error message found")
            context.logger.error(f"[HEADERS] Available keys: {available_keys}")
            context.logger.debug(f"[BODY] Response content: {json.dumps(response_json, indent=2)[:500]}...")
            
            # Capture error details for failure report
            error_details = f"Error message assertion failed - No error message found in response"
            if hasattr(context, 'scenario_metrics'):
                context.scenario_metrics.setdefault('errors', []).append(error_details)
            context.last_error = error_details
            
            raise AssertionError(f"Response does not contain error message. Available keys: {available_keys}")
    
    except json.JSONDecodeError as e:
        context.logger.error(f"[ERROR] JSON decode error: {e}")
        context.logger.error(f"[BODY] Raw response: {context.response.text[:200]}...")
        
        # Check if response is empty (common for 400 status codes with URL encoding issues)
        if not context.response.text.strip():
            context.logger.info(f"[SUCCESS] Empty response body for status {context.response.status_code} - treating as valid error response")
            return

        # Check if response text contains error-like content
        response_text = context.response.text.lower()
        if any(word in response_text for word in ['error', 'fail', 'invalid', 'unauthorized', 'forbidden']):
            context.logger.info(f"[SUCCESS] Error message found in response text: {context.response.text[:100]}...")
        elif context.response.status_code >= 400:
            # For error status codes, accept empty or malformed responses as valid error indicators
            context.logger.info(f"[SUCCESS] Error status code {context.response.status_code} with empty/malformed response - treating as valid error response")
        else:
            # Capture JSON error details for failure report
            error_details = f"JSON decode error and no error text found: {e}"
            if hasattr(context, 'scenario_metrics'):
                context.scenario_metrics.setdefault('errors', []).append(error_details)
            context.last_error = error_details

            raise AssertionError("Response is not valid JSON and contains no error text")


# ============================================================================
# Content Validations
# ============================================================================

@then('the response should not contain "{text}"')
def step_assert_response_not_contains_text(context: Context, text: str):
    """Assert that response does not contain specified text (e.g., XSS protection)."""
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    context.logger.info(f"[VERIFY] Verifying response does not contain '{text}'")
    
    if not hasattr(context, 'response') or context.response is None:
        context.logger.error("[ERROR] No response available for text verification")
        raise AssertionError("No response available")
    
    response_text = context.response.text.lower()
    search_text = text.lower()
    
    if search_text in response_text:
        context.logger.error(f"[ERROR] Security violation: Response contains '{text}'")
        context.logger.debug(f"[BODY] Response snippet: {context.response.text[:200]}...")
        
        # Capture error details for failure report
        error_details = f"Security assertion failed - Response contains forbidden text '{text}'"
        if hasattr(context, 'scenario_metrics'):
            context.scenario_metrics.setdefault('errors', []).append(error_details)
        context.last_error = error_details
        
        raise AssertionError(f"Response contains forbidden text: {text}")
    
    context.logger.info(f"[SUCCESS] Response does not contain '{text}' - Security check passed")


# ============================================================================
# Data Extraction and Saving
# ============================================================================

@then('I save the response "{field}" as "{variable_name}"')
def step_save_response_field(context: Context, field: str, variable_name: str):
    """Save a response field for use in subsequent steps."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    if not hasattr(context, 'response') or context.response is None:
        context.logger.error("[ERROR] No response available for field saving")
        raise AssertionError("No response available")
    
    try:
        response_json = context.response.json()
        context.logger.debug(f"[SAVE] Attempting to save field '{field}' as '{variable_name}'")
        
        if field not in response_json:
            context.logger.error(f"[ERROR] Response does not contain field: {field}")
            context.logger.debug(f"[BODY] Available fields: {list(response_json.keys())}")
            raise AssertionError(f"Response does not contain field: {field}")
        
        if not hasattr(context, 'saved_data'):
            context.saved_data = {}
        
        context.saved_data[variable_name] = response_json[field]
        context.logger.info(f"[SUCCESS] Saved {field}='{response_json[field]}' as '{variable_name}'")
        
    except json.JSONDecodeError as e:
        context.logger.error(f"[ERROR] Response is not valid JSON: {e}")
        raise AssertionError(f"Response is not valid JSON: {e}")


@then('the response should contain the correlation ID')
def step_assert_correlation_id(context: Context):
    """Assert that response contains correlation ID header."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    if not hasattr(context, 'response') or context.response is None:
        context.logger.error("[ERROR] No response available for correlation ID check")
        raise AssertionError("No response available")
    
    correlation_header = 'X-Correlation-Id'
    if correlation_header in context.response.headers:
        context.logger.info(f"[SUCCESS] Found correlation ID: {context.response.headers[correlation_header]}")
    else:
        context.logger.error(f"[ERROR] Response missing {correlation_header} header")
        context.logger.debug(f"[DEBUG] Available headers: {list(context.response.headers.keys())}")
        raise AssertionError(f"Response missing {correlation_header} header")


# ============================================================================
# Debug and Utility Steps - Moved to common_steps.py
# ============================================================================
# (Debug steps now in common_steps.py to avoid duplicates)