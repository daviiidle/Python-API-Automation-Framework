"""
Common utilities and shared helper functions for Banking API BDD tests.
Contains shared utilities used across multiple step definition files.
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from behave import given, when, then, step
from behave.runner import Context


# ============================================================================
# Shared Logger Setup and Environment Configuration
# ============================================================================

def setup_fallback_logger(context: Context):
    """Setup a basic logger if environment.py didn't run properly."""
    # Only setup once per context
    if hasattr(context, 'logger') and context.logger:
        return
    
    # Load environment variables from .env file
    load_environment_config(context)
    
    # Create logs directory
    try:
        os.makedirs('logs', exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create logs directory: {e}")
    
    # Setup basic logging
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = f"logs/banking_api_tests_{timestamp}.log"
    
    # Get log level from environment
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    numeric_level = getattr(logging, log_level, logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Setup logger with unique name to avoid conflicts
    logger_name = f'banking_api_fallback_{timestamp}'
    logger = logging.getLogger(logger_name)
    logger.setLevel(numeric_level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (with error handling)
    try:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not create log file handler: {e}")
    
    # Set up context with environment variables
    context.logger = logger
    context.log_file = log_file
    
    # Initialize metrics if not already present
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
    
    logger.warning("[WARNING] Using fallback logger - environment.py hooks may not be working properly")
    logger.info("[FRAMEWORK] Banking API BDD Framework - Fallback initialization complete")
    logger.info(f"[ENV] Environment: {os.getenv('TEST_ENVIRONMENT', os.getenv('ENVIRONMENT', 'dev'))}")
    logger.info(f"[URL] Base URL: {context.base_url}")
    logger.info(f"[FILE] Log file: {log_file}")


def load_environment_config(context: Context):
    """Load configuration from environment variables and .env files."""
    # Determine environment
    environment = os.getenv('TEST_ENVIRONMENT', os.getenv('ENVIRONMENT', 'dev'))
    
    # Try to load from .env file for the specific environment
    env_file_path = f"environments/.env.{environment}"
    if os.path.exists(env_file_path):
        # Simple .env file parser (since we're avoiding extra dependencies)
        with open(env_file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Only set if not already in environment
                    if key not in os.environ:
                        os.environ[key] = value
    
    # Set context variables from environment
    context.environment = environment
    context.base_url = os.getenv('BASE_URL', 'http://localhost:8080')
    context.auth_token = os.getenv('AUTH_TOKEN', 'banking-api-key-2024')
    context.timeout = int(os.getenv('TIMEOUT', '30'))
    context.request_timeout = int(os.getenv('REQUEST_TIMEOUT', '10'))
    context.retry_count = int(os.getenv('RETRY_COUNT', '3'))
    context.correlation_id_header = os.getenv('CORRELATION_ID_HEADER', 'X-Correlation-Id')
    context.content_type = os.getenv('CONTENT_TYPE', 'application/json')
    context.auth_header = os.getenv('AUTH_HEADER', 'Authorization')
    context.auth_prefix = os.getenv('AUTH_PREFIX', 'Bearer')
    context.performance_threshold_ms = int(os.getenv('PERFORMANCE_THRESHOLD_MS', '2000'))
    
    # Setup auth headers
    context.auth_headers = {
        context.auth_header: f"{context.auth_prefix} {context.auth_token}",
        'Content-Type': context.content_type
    }


# ============================================================================
# Shared Utility Functions
# ============================================================================

def ensure_logger_available(context: Context):
    """Ensure logger is available in context, setup fallback if needed."""
    if not hasattr(context, 'logger'):
        setup_fallback_logger(context)


def update_metrics(context: Context, response_time: float):
    """Update test and scenario metrics with API call data."""
    if hasattr(context, 'test_metrics'):
        context.test_metrics['api_calls'] += 1
        context.test_metrics['total_response_time'] += response_time
    
    if hasattr(context, 'scenario_metrics'):
        context.scenario_metrics['api_calls'] += 1
        context.scenario_metrics['total_response_time'] += response_time


def log_response_details(context: Context, response, response_time: float, request_type: str = ""):
    """Log standardized response details."""
    context.logger.info(f"[RESPONSE] {request_type} Response: {response.status_code}")
    context.logger.info(f"[TIME] Response Time: {response_time:.3f}s")
    context.logger.debug(f"[HEADERS] Response Headers: {dict(response.headers)}")
    
    # Log response body (limited for readability)
    try:
        if response.headers.get('content-type', '').startswith('application/json'):
            response_body = response.json()
            context.logger.debug(f"[BODY] Response Body: {json.dumps(response_body, indent=2)[:500]}...")
        else:
            context.logger.debug(f"[BODY] Response Body: {response.text[:200]}...")
    except Exception:
        context.logger.debug(f"[BODY] Response Body (raw): {response.text[:200]}...")


def capture_error_details(context: Context, error_message: str):
    """Capture error details for failure reporting."""
    if hasattr(context, 'scenario_metrics'):
        context.scenario_metrics.setdefault('errors', []).append(error_message)
    context.last_error = error_message


def mask_sensitive_value(value: str, mask_length: int = 4) -> str:
    """Mask sensitive values for logging (e.g., tokens, passwords)."""
    if not value or len(value) <= mask_length:
        return "****"
    return f"{'*' * (len(value) - mask_length)}{value[-mask_length:]}"


def safe_json_parse(text: str) -> Optional[dict]:
    """Safely parse JSON text, returning None if invalid."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def extract_field_from_response(response, field_name: str) -> Optional[Any]:
    """Extract a specific field from JSON response safely."""
    try:
        response_json = response.json()
        return response_json.get(field_name)
    except (json.JSONDecodeError, AttributeError):
        return None


# ============================================================================
# Debug and Utility Steps (Keep these for backward compatibility)
# ============================================================================

@step('I print the response')
def step_print_response(context: Context):
    """Print response for debugging purposes."""
    if hasattr(context, 'response') and context.response:
        print(f"Status: {context.response.status_code}")
        print(f"Headers: {dict(context.response.headers)}")
        print(f"Body: {context.response.text}")
    else:
        print("No response available")


@step('I print the saved data')
def step_print_saved_data(context: Context):
    """Print saved data for debugging purposes."""
    if hasattr(context, 'saved_data'):
        print(f"Saved data: {context.saved_data}")
    else:
        print("No saved data available")


@step('steps are loaded correctly')
def step_debug_loaded(context: Context):
    """Debug step to verify step definitions are being loaded."""
    print("✅ Step definitions are loaded correctly!")


# ============================================================================
# Context Validation Utilities
# ============================================================================

def validate_required_context(context: Context, required_attrs: list) -> bool:
    """Validate that context has all required attributes."""
    missing_attrs = []
    for attr in required_attrs:
        if not hasattr(context, attr):
            missing_attrs.append(attr)
    
    if missing_attrs:
        ensure_logger_available(context)
        context.logger.error(f"[ERROR] Missing required context attributes: {missing_attrs}")
        return False
    
    return True


def get_context_value(context: Context, attr_name: str, default_value: Any = None) -> Any:
    """Safely get a value from context with fallback to default."""
    return getattr(context, attr_name, default_value)


# ============================================================================
# Response Helper Functions
# ============================================================================

def is_successful_response(response) -> bool:
    """Check if response status code indicates success (2xx)."""
    return 200 <= response.status_code < 300


def is_client_error_response(response) -> bool:
    """Check if response status code indicates client error (4xx)."""
    return 400 <= response.status_code < 500


def is_server_error_response(response) -> bool:
    """Check if response status code indicates server error (5xx)."""
    return 500 <= response.status_code < 600


def get_error_message_from_response(response) -> Optional[str]:
    """Extract error message from response if available."""
    try:
        response_json = response.json()
        error_keys = ['error', 'message', 'errorMessage', 'error_message', 'details']
        
        for key in error_keys:
            if key in response_json:
                return str(response_json[key])
        
        return None
    except (json.JSONDecodeError, AttributeError):
        return None


# ============================================================================
# Data Validation Helpers
# ============================================================================

def validate_email_format(email: str) -> bool:
    """Basic email format validation."""
    return '@' in email and '.' in email.split('@')[1]


def validate_phone_format(phone: str) -> bool:
    """Basic phone format validation."""
    return phone.startswith('+') or phone.startswith('0')


def validate_positive_amount(amount: Any) -> bool:
    """Validate that amount is positive number."""
    try:
        return float(amount) >= 0
    except (ValueError, TypeError):
        return False


def validate_date_format(date_str: str, expected_format: str = '%Y-%m-%d') -> bool:
    """Validate date string format."""
    try:
        datetime.strptime(date_str, expected_format)
        return True
    except ValueError:
        return False


# ============================================================================
# Request Building Helpers
# ============================================================================

def build_standard_headers(context: Context, additional_headers: Dict[str, str] = None) -> Dict[str, str]:
    """Build standard request headers with optional additions."""
    headers = getattr(context, 'auth_headers', {}).copy()
    
    if additional_headers:
        headers.update(additional_headers)
    
    return headers


def build_request_url(context: Context, endpoint: str) -> str:
    """Build full request URL from base URL and endpoint."""
    base_url = getattr(context, 'base_url', 'http://localhost:8080')
    return f"{base_url.rstrip('/')}{endpoint}"


# ============================================================================
# Test Data Helpers
# ============================================================================

def get_test_data_for_type(context: Context, data_type: str) -> Optional[Dict[str, Any]]:
    """Get test data for specific type from context."""
    if not hasattr(context, 'test_data'):
        return None
    
    test_data = context.test_data
    
    # Check for exact match first, then variations
    if data_type in test_data:
        return test_data[data_type]
    elif f'boundary_{data_type}' in test_data:
        return test_data[f'boundary_{data_type}']
    elif f'invalid_{data_type}' in test_data:
        return test_data[f'invalid_{data_type}']
    
    return None


def save_response_field_to_context(context: Context, response, field_name: str, variable_name: str) -> bool:
    """Save a field from response to context for later use."""
    try:
        response_json = response.json()
        if field_name not in response_json:
            return False
        
        if not hasattr(context, 'saved_data'):
            context.saved_data = {}
        
        context.saved_data[variable_name] = response_json[field_name]
        return True
    except (json.JSONDecodeError, AttributeError):
        return False