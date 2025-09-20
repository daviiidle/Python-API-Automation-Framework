"""
HTTP operation step definitions for Banking API BDD tests.
Handles all HTTP method operations: GET, POST, PUT, DELETE, PATCH.
"""

import json
import time
import requests
from typing import Dict, Any

from behave import given, when, then, step
from behave.runner import Context


# ============================================================================
# HTTP Method Step Definitions
# ============================================================================

@when('I send a GET request to "{endpoint}"')
def step_get_request(context: Context, endpoint: str):
    """Send GET request to specified endpoint."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    base_url = context.base_url
    headers = context.auth_headers.copy()  # Copy to avoid modifying original
    timeout = context.request_timeout
    
    full_url = f"{base_url.rstrip('/')}{endpoint}"
    
    context.logger.info(f"[REQUEST] Sending GET request to: {endpoint}")
    context.logger.debug(f"[URL] Full URL: {full_url}")
    context.logger.debug(f"[HEADERS] Request Headers: {dict(headers)}")
    
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
        context.logger.info(f"[RESPONSE] GET Response: {context.response.status_code}")
        context.logger.info(f"[TIME] Response Time: {response_time:.3f}s")
        context.logger.debug(f"[HEADERS] Response Headers: {dict(context.response.headers)}")
        
        # Log response body (limited for readability)
        try:
            if context.response.headers.get('content-type', '').startswith('application/json'):
                response_body = context.response.json()
                context.logger.debug(f"[BODY] Response Body: {json.dumps(response_body, indent=2)[:500]}...")
            else:
                context.logger.debug(f"[BODY] Response Body: {context.response.text[:200]}...")
        except Exception:
            context.logger.debug(f"[BODY] Response Body (raw): {context.response.text[:200]}...")
        
        context.logger.info(f"[SUCCESS] GET request completed successfully")
        
    except requests.exceptions.Timeout:
        context.logger.error(f"[TIMEOUT] GET request to {endpoint} timed out")
        context.response = None
        context.last_error = "Request timeout"
        raise AssertionError(f"Request to {endpoint} timed out")
    except requests.exceptions.ConnectionError as e:
        context.logger.error(f"[CONNECTION] Connection error for GET {endpoint}: {e}")
        context.response = None
        context.last_error = str(e)
        raise AssertionError(f"Connection error: {e}")
    except Exception as e:
        context.logger.error(f"[ERROR] GET request failed: {e}")
        context.response = None
        context.last_error = str(e)
        raise AssertionError(f"Request failed: {e}")


@when('I send a GET request to "{endpoint}" with substitution')
def step_get_request_with_substitution(context: Context, endpoint: str):
    """Send GET request to endpoint with variable substitution from saved data."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    # Substitute saved variables in endpoint
    if hasattr(context, 'saved_data') and context.saved_data:
        for var_name, var_value in context.saved_data.items():
            placeholder = "{" + var_name + "}"
            if placeholder in endpoint:
                endpoint = endpoint.replace(placeholder, str(var_value))
                context.logger.debug(f"[SUBSTITUTE] Replaced {placeholder} with {var_value}")
    
    context.logger.debug(f"[ENDPOINT] Final endpoint after substitution: {endpoint}")
    
    # Use the existing GET request logic
    step_get_request(context, endpoint)


@when('I send a POST request to "{endpoint}"')
def step_post_request(context: Context, endpoint: str):
    """Send POST request to specified endpoint."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    base_url = context.base_url
    headers = context.auth_headers.copy()  # Copy to avoid modifying original
    timeout = context.request_timeout
    
    # Use test data if available, otherwise sample data
    data = getattr(context, 'request_body', {
        "customerId": "CUST001",
        "accountType": "SAVINGS",
        "currency": "AUD",
        "initialBalance": 1000.00
    })
    
    full_url = f"{base_url.rstrip('/')}{endpoint}"
    
    context.logger.info(f"[REQUEST] Sending POST request to: {endpoint}")
    context.logger.debug(f"[URL] Full URL: {full_url}")
    context.logger.debug(f"[HEADERS] Request Headers: {dict(headers)}")
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
        context.logger.info(f"[RESPONSE] POST Response: {context.response.status_code}")
        context.logger.info(f"[TIME] Response Time: {response_time:.3f}s")
        context.logger.debug(f"[HEADERS] Response Headers: {dict(context.response.headers)}")
        
        # Log response body (limited for readability)
        try:
            if context.response.headers.get('content-type', '').startswith('application/json'):
                response_body = context.response.json()
                context.logger.debug(f"[BODY] Response Body: {json.dumps(response_body, indent=2)[:500]}...")
            else:
                context.logger.debug(f"[BODY] Response Body: {context.response.text[:200]}...")
        except Exception:
            context.logger.debug(f"[BODY] Response Body (raw): {context.response.text[:200]}...")
        
        context.logger.info(f"[SUCCESS] POST request completed successfully")
        
    except requests.exceptions.Timeout:
        context.logger.error(f"[TIMEOUT] POST request to {endpoint} timed out")
        context.response = None
        context.last_error = "Request timeout"
        raise AssertionError(f"Request to {endpoint} timed out")
    except requests.exceptions.ConnectionError as e:
        context.logger.error(f"[CONNECTION] Connection error for POST {endpoint}: {e}")
        context.response = None
        context.last_error = str(e)
        raise AssertionError(f"Connection error: {e}")
    except Exception as e:
        context.logger.error(f"[ERROR] POST request failed: {e}")
        context.response = None
        context.last_error = str(e)
        raise AssertionError(f"Request failed: {e}")


@when('I send a POST request to "{endpoint}" with data:')
def step_post_request_with_data(context: Context, endpoint: str):
    """Send POST request to specified endpoint with data from context.text."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    base_url = context.base_url
    headers = getattr(context, 'auth_headers', {})
    
    # Only set Content-Type if not already set by custom headers
    if 'Content-Type' not in headers:
        headers['Content-Type'] = 'application/json'
    timeout = getattr(context, 'request_timeout', 10)
    
    # Parse JSON data from context.text - allow invalid JSON for testing
    try:
        data = json.loads(context.text) if context.text else {}
        
        # Replace hardcoded customer IDs with dynamic timestamp-based IDs to avoid conflicts
        if data and isinstance(data, dict) and data.get('customerId'):
            customer_id = data.get('customerId')
            # Check if it's a hardcoded customer ID that could cause conflicts
            hardcoded_patterns = ['CUST001', 'CUST002', 'CUST003', 'CUST999']

            if customer_id in hardcoded_patterns:
                # Use existing unique customer ID if available, or generate new timestamp-based ID
                if hasattr(context, 'unique_customer_id'):
                    dynamic_customer_id = context.unique_customer_id
                else:
                    from datetime import datetime
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
                    dynamic_customer_id = f"CUST_DYN_{timestamp}"

                data['customerId'] = dynamic_customer_id
                context.logger.info(f"[DATA] Replaced hardcoded {customer_id} with dynamic ID: {dynamic_customer_id}")
        
        context.logger.debug(f"[BODY] Parsed request data: {json.dumps(data, indent=2)}")
        request_body = json.dumps(data)
    except json.JSONDecodeError as e:
        context.logger.warning(f"[WARN] Invalid JSON detected - sending raw data for testing: {e}")
        # For invalid JSON tests, send the raw text instead of parsed JSON
        data = None
        request_body = context.text
    
    full_url = f"{base_url.rstrip('/')}{endpoint}"
    
    context.logger.info(f"[REQUEST] Sending POST request to: {endpoint}")
    context.logger.debug(f"[URL] Full URL: {full_url}")
    context.logger.debug(f"[HEADERS] Request Headers: {dict(headers)}")
    if data is not None:
        context.logger.debug(f"[BODY] Request Body: {json.dumps(data, indent=2)}")
    else:
        context.logger.debug(f"[BODY] Raw Request Body: {request_body}")
    
    try:
        start_time = time.time()
        if data is not None:
            context.response = requests.post(full_url, headers=headers, json=data, timeout=timeout)
        else:
            # Send raw data for invalid JSON testing
            context.response = requests.post(full_url, headers=headers, data=request_body, timeout=timeout)
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
        context.logger.info(f"[RESPONSE] POST Response: {context.response.status_code}")
        context.logger.info(f"[TIME] Response Time: {response_time:.3f}s")
        context.logger.debug(f"[HEADERS] Response Headers: {dict(context.response.headers)}")
        
        # Log response body (limited for readability)
        try:
            if context.response.headers.get('content-type', '').startswith('application/json'):
                response_json = context.response.json()
                context.logger.debug(f"[BODY] Response JSON: {json.dumps(response_json, indent=2)[:500]}...")
            else:
                context.logger.debug(f"[BODY] Response Body: {context.response.text[:300]}...")
        except Exception:
            context.logger.debug(f"[BODY] Response Body (text): {context.response.text[:300]}...")
        
    except requests.exceptions.Timeout:
        context.logger.error(f"[TIMEOUT] POST request to {endpoint} timed out")
        context.last_error = f"POST request to {endpoint} timed out"
        raise AssertionError(f"Request timeout")
    except requests.exceptions.ConnectionError as e:
        context.logger.error(f"[CONNECTION] Connection error during POST to {endpoint}: {e}")
        context.last_error = f"Connection error during POST: {e}"
        raise AssertionError(f"Connection error: {e}")
    except Exception as e:
        context.logger.error(f"[ERROR] POST request failed: {e}")
        context.response = None
        context.last_error = str(e)
        raise AssertionError(f"Request failed: {e}")


@when('I send a PUT request to "{endpoint}"')
def step_put_request(context: Context, endpoint: str):
    """Send PUT request to specified endpoint."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    base_url = context.base_url
    headers = getattr(context, 'auth_headers', {})
    headers['Content-Type'] = 'application/json'
    timeout = getattr(context, 'request_timeout', 10)
    
    # Use test data if available, otherwise sample data
    data = getattr(context, 'request_body', {
        "customerId": "CUST001",
        "accountType": "SAVINGS",
        "currency": "AUD"
    })
    
    full_url = f"{base_url.rstrip('/')}{endpoint}"
    
    context.logger.info(f"[REQUEST] Sending PUT request to: {endpoint}")
    context.logger.debug(f"[URL] Full URL: {full_url}")
    context.logger.debug(f"[HEADERS] Request Headers: {dict(headers)}")
    context.logger.debug(f"[BODY] Request Body: {json.dumps(data, indent=2)}")
    
    try:
        start_time = time.time()
        context.response = requests.put(full_url, headers=headers, json=data, timeout=timeout)
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
        context.logger.info(f"[RESPONSE] PUT Response: {context.response.status_code}")
        context.logger.info(f"[TIME] Response Time: {response_time:.3f}s")
        context.logger.debug(f"[HEADERS] Response Headers: {dict(context.response.headers)}")
        
    except requests.exceptions.Timeout:
        context.logger.error(f"[TIMEOUT] PUT request to {endpoint} timed out")
        context.last_error = f"PUT request to {endpoint} timed out"
        raise AssertionError(f"Request timeout")
    except Exception as e:
        context.logger.error(f"[ERROR] PUT request failed: {e}")
        context.response = None
        context.last_error = str(e)
        raise AssertionError(f"Request failed: {e}")


@when('I send a DELETE request to "{endpoint}"')
def step_delete_request(context: Context, endpoint: str):
    """Send DELETE request to specified endpoint."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    base_url = context.base_url
    headers = getattr(context, 'auth_headers', {})
    timeout = getattr(context, 'request_timeout', 10)
    
    full_url = f"{base_url.rstrip('/')}{endpoint}"
    
    context.logger.info(f"[REQUEST] Sending DELETE request to: {endpoint}")
    context.logger.debug(f"[URL] Full URL: {full_url}")
    context.logger.debug(f"[HEADERS] Request Headers: {dict(headers)}")
    
    try:
        start_time = time.time()
        context.response = requests.delete(full_url, headers=headers, timeout=timeout)
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
        context.logger.info(f"[RESPONSE] DELETE Response: {context.response.status_code}")
        context.logger.info(f"[TIME] Response Time: {response_time:.3f}s")
        context.logger.debug(f"[HEADERS] Response Headers: {dict(context.response.headers)}")
        
    except requests.exceptions.Timeout:
        context.logger.error(f"[TIMEOUT] DELETE request to {endpoint} timed out")
        context.last_error = f"DELETE request to {endpoint} timed out"
        raise AssertionError(f"Request timeout")
    except Exception as e:
        context.logger.error(f"[ERROR] DELETE request failed: {e}")
        context.response = None
        context.last_error = str(e)
        raise AssertionError(f"Request failed: {e}")


@when('I send a PATCH request to "{endpoint}"')
def step_patch_request(context: Context, endpoint: str):
    """Send PATCH request to specified endpoint."""
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    base_url = context.base_url
    headers = context.auth_headers.copy()
    timeout = context.request_timeout
    
    full_url = f"{base_url.rstrip('/')}{endpoint}"
    
    context.logger.info(f"[REQUEST] Sending PATCH request to: {endpoint}")
    context.logger.debug(f"[URL] Full URL: {full_url}")
    
    try:
        start_time = time.time()
        context.response = requests.patch(full_url, headers=headers, timeout=timeout)
        response_time = time.time() - start_time
        
        # Update metrics
        if hasattr(context, 'test_metrics'):
            context.test_metrics['api_calls'] += 1
            context.test_metrics['total_response_time'] += response_time
        if hasattr(context, 'scenario_metrics'):
            context.scenario_metrics['api_calls'] += 1
            context.scenario_metrics['total_response_time'] += response_time
        
        context.logger.info(f"[RESPONSE] PATCH Response: {context.response.status_code}")
        context.logger.info(f"[TIME] Response Time: {response_time:.3f}s")
        
    except requests.exceptions.RequestException as e:
        context.logger.error(f"[ERROR] PATCH request failed: {e}")
        raise AssertionError(f"PATCH request failed: {e}")


# ============================================================================
# Request Body and Header Management
# ============================================================================

@when('I set the request body to')
def step_set_request_body(context: Context):
    """Set request body from context text."""
    if context.text:
        try:
            context.request_body = json.loads(context.text)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON in request body")


@step('I set the "{header}" header to "{value}"')
def step_set_header(context: Context, header: str, value: str):
    """Set a specific header for the next request."""
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    context.logger.info(f"[HEADER] Setting custom header: {header} = {value}")
    
    if not hasattr(context, 'custom_headers'):
        context.custom_headers = {}
    context.custom_headers[header] = value
    
    # Apply custom header to auth_headers for immediate use
    if hasattr(context, 'auth_headers'):
        context.auth_headers[header] = value
    else:
        # Initialize auth_headers if it doesn't exist
        context.auth_headers = {header: value}


@when('I send a request without authentication')
def step_request_without_auth(context: Context):
    """Remove authentication for the next request."""
    # Ensure logger is available
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    # Store original headers to restore later
    if hasattr(context, 'auth_headers'):
        context.original_auth_headers = context.auth_headers.copy()
        # Remove Authorization header temporarily
        if 'Authorization' in context.auth_headers:
            del context.auth_headers['Authorization']
            context.logger.info("[AUTH] Temporarily removed Authorization header")
    else:
        context.logger.warning("[WARN] No auth headers to remove")


@when('I send a request with malformed Authorization header')
def step_malformed_auth_header(context: Context):
    """Send request with malformed authorization header."""
    if not hasattr(context, 'logger'):
        from .common_steps import setup_fallback_logger
        setup_fallback_logger(context)
    
    # Store original headers
    if hasattr(context, 'auth_headers'):
        context.original_auth_headers = context.auth_headers.copy()
    
    # Set malformed auth header
    context.auth_headers = context.auth_headers.copy()
    context.auth_headers['Authorization'] = 'Malformed auth header'
    
    context.logger.info("[AUTH] Set malformed Authorization header")