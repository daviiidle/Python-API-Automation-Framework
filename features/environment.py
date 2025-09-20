"""
Comprehensive Behave environment configuration for Banking API BDD tests with detailed logging.
"""

import os
import logging
import json
import traceback
from datetime import datetime


def setup_comprehensive_logging(context):
    """Setup comprehensive logging for the test framework."""
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Setup file logging with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = f"logs/banking_api_tests_{timestamp}.log"
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Create context logger
    context.logger = logging.getLogger('banking_api_tests')
    context.log_file = log_file
    
    return context.logger


def capture_failure_details(context, scenario, end_time, duration):
    """Capture detailed failure information to a separate file."""
    # Create failures directory
    os.makedirs('logs/failures', exist_ok=True)
    
    # Generate failure file name with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_scenario_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in scenario.name)
    safe_scenario_name = safe_scenario_name.replace(' ', '_')[:50]  # Limit length
    failure_file = f"logs/failures/FAILED_{safe_scenario_name}_{timestamp}.txt"
    
    # Collect failure details
    failure_details = {
        'timestamp': end_time.isoformat(),
        'scenario': scenario.name,
        'feature': scenario.feature.name,
        'location': str(scenario.location),
        'duration': str(duration),
        'tags': list(scenario.tags) if scenario.tags else [],
        'status': scenario.status.name if hasattr(scenario.status, 'name') else str(scenario.status)
    }
    
    # Get exception details if available
    if hasattr(scenario, 'exception') and scenario.exception:
        failure_details['exception'] = {
            'type': type(scenario.exception).__name__,
            'message': str(scenario.exception),
            'traceback': traceback.format_exception(type(scenario.exception), scenario.exception, scenario.exception.__traceback__)
        }
    
    # Get last error from context if available
    if hasattr(context, 'last_error') and context.last_error:
        failure_details['last_error'] = context.last_error
    
    # Get API response details if available
    if hasattr(context, 'response') and context.response:
        try:
            failure_details['api_response'] = {
                'status_code': context.response.status_code,
                'headers': dict(context.response.headers),
                'url': context.response.url,
                'body': context.response.text[:2000] + "..." if len(context.response.text) > 2000 else context.response.text
            }
        except Exception as e:
            failure_details['api_response_error'] = f"Could not capture response: {e}"
    
    # Get scenario metrics if available
    if hasattr(context, 'scenario_metrics'):
        failure_details['metrics'] = context.scenario_metrics
    
    # Get environment details
    failure_details['environment'] = {
        'base_url': getattr(context, 'base_url', 'Not set'),
        'test_environment': os.getenv('TEST_ENVIRONMENT', 'Not set'),
        'working_directory': os.getcwd()
    }
    
    # Write detailed failure report
    try:
        with open(failure_file, 'w') as f:
            f.write("[ERROR] BANKING API BDD FRAMEWORK - TEST FAILURE REPORT [ERROR]\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"[TIME] Failure Time: {failure_details['timestamp']}\n")
            f.write(f"[TEST] Scenario: {failure_details['scenario']}\n")
            f.write(f"[FILE] Feature: {failure_details['feature']}\n")
            f.write(f"[LOCATION] Location: {failure_details['location']}\n")
            f.write(f"[TIME]  Duration: {failure_details['duration']}\n")
            f.write(f"[TAGS]  Tags: {', '.join(failure_details['tags']) if failure_details['tags'] else 'None'}\n")
            f.write(f"[INFO] Status: {failure_details['status']}\n\n")
            
            # Exception details
            if 'exception' in failure_details:
                f.write("[ERROR] EXCEPTION DETAILS:\n")
                f.write("-" * 40 + "\n")
                f.write(f"Type: {failure_details['exception']['type']}\n")
                f.write(f"Message: {failure_details['exception']['message']}\n\n")
                f.write("Traceback:\n")
                for line in failure_details['exception']['traceback']:
                    f.write(line)
                f.write("\n")
            
            # Last error
            if 'last_error' in failure_details:
                f.write(f"[ERROR] Last Error: {failure_details['last_error']}\n\n")
            
            # API Response details
            if 'api_response' in failure_details:
                f.write("[URL] API RESPONSE DETAILS:\n")
                f.write("-" * 40 + "\n")
                f.write(f"Status Code: {failure_details['api_response']['status_code']}\n")
                f.write(f"URL: {failure_details['api_response']['url']}\n")
                f.write(f"Headers: {json.dumps(failure_details['api_response']['headers'], indent=2)}\n")
                f.write(f"Response Body:\n{failure_details['api_response']['body']}\n\n")
            
            # Metrics
            if 'metrics' in failure_details:
                f.write("[INFO] SCENARIO METRICS:\n")
                f.write("-" * 40 + "\n")
                f.write(f"API Calls: {failure_details['metrics'].get('api_calls', 0)}\n")
                f.write(f"Total Response Time: {failure_details['metrics'].get('total_response_time', 0):.3f}s\n")
                if failure_details['metrics'].get('errors'):
                    f.write(f"Errors: {failure_details['metrics']['errors']}\n")
                f.write("\n")
            
            # Environment
            f.write("[ENV] ENVIRONMENT DETAILS:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Base URL: {failure_details['environment']['base_url']}\n")
            f.write(f"Test Environment: {failure_details['environment']['test_environment']}\n")
            f.write(f"Working Directory: {failure_details['environment']['working_directory']}\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("[BODY] This file contains detailed failure information for debugging.\n")
            f.write("[VERIFY] Review the exception details and API response for troubleshooting.\n")
            f.write("=" * 80 + "\n")
    
        # Log that failure was captured
        context.logger.error(f"[SAVE] Failure details saved to: {failure_file}")
        
        # Store failure file reference in context
        if not hasattr(context, 'failure_files'):
            context.failure_files = []
        context.failure_files.append(failure_file)
        
    except Exception as e:
        context.logger.error(f"[ERROR] Failed to save failure details: {e}")


def create_failure_summary(context, end_time, failed_count):
    """Create a summary file of all failures for quick review."""
    timestamp = end_time.strftime('%Y%m%d_%H%M%S')
    summary_file = f"logs/failures/FAILURE_SUMMARY_{timestamp}.txt"
    
    try:
        with open(summary_file, 'w') as f:
            f.write("[ERROR] BANKING API BDD FRAMEWORK - FAILURE SUMMARY [ERROR]\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"[TIME] Summary Generated: {end_time.isoformat()}\n")
            f.write(f"[FAILED] Total Failed Scenarios: {failed_count}\n")
            f.write(f"[HEADERS] Individual Failure Files: {len(context.failure_files)}\n\n")
            
            f.write("[BODY] QUICK FAILURE OVERVIEW:\n")
            f.write("-" * 50 + "\n")
            
            for i, failure_file in enumerate(context.failure_files, 1):
                # Extract scenario name from filename
                filename = os.path.basename(failure_file)
                scenario_part = filename.replace('FAILED_', '').replace('.txt', '')
                # Remove timestamp from end
                scenario_name = '_'.join(scenario_part.split('_')[:-2]) if '_' in scenario_part else scenario_part
                
                f.write(f"{i:2d}. {scenario_name.replace('_', ' ')}\n")
                f.write(f"    [BODY] Details: {failure_file}\n\n")
            
            f.write("-" * 50 + "\n")
            f.write("[VERIFY] TROUBLESHOOTING STEPS:\n")
            f.write("1. Review individual failure files above for detailed error information\n")
            f.write("2. Check API response details and status codes\n")
            f.write("3. Verify environment configuration and connectivity\n")
            f.write("4. Review exception tracebacks for code issues\n")
            f.write("5. Check authentication and authorization settings\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("[SUPPORT] For support, review the detailed failure files listed above.\n")
            f.write("=" * 80 + "\n")
        
        context.logger.error(f"[HEADERS] Failure summary created: {summary_file}")
        
    except Exception as e:
        context.logger.error(f"[ERROR] Failed to create failure summary: {e}")


def load_environment_config(context):
    """Load environment variables from .env files."""
    env_name = os.getenv('ENVIRONMENT', os.getenv('TEST_ENVIRONMENT', 'test'))
    
    # Map of environment names to .env files
    env_files = {
        'test': 'environments/.env.test',
        'dev': 'environments/.env.dev', 
        'staging': 'environments/.env.staging',
        'railway': 'environments/.env.railway',
        'prod': 'environments/.env.prod'
    }
    
    # Load the appropriate .env file
    env_file = env_files.get(env_name, 'environments/.env.test')
    
    context.logger.info(f"[ENV] Loading environment: {env_name}")
    context.logger.info(f"[FILE] Environment file: {env_file}")
    
    if os.path.exists(env_file):
        # Read .env file manually (simple implementation)
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        os.environ[key] = value
            context.logger.info(f"[ENV] Successfully loaded {env_file}")
        except Exception as e:
            context.logger.error(f"[ERROR] Failed to load {env_file}: {e}")
            context.logger.warning(f"[WARNING] Using system environment variables and defaults")
    else:
        context.logger.warning(f"[WARNING] Environment file {env_file} not found")
        context.logger.warning(f"[WARNING] Using system environment variables and defaults")


def before_all(context):
    """Hook that runs before all tests."""
    # Setup comprehensive logging first
    logger = setup_comprehensive_logging(context)
    
    # Log test execution start
    logger.info("[FRAMEWORK] " + "=" * 80)
    logger.info("[FRAMEWORK] BANKING API BDD TEST FRAMEWORK - EXECUTION START")
    logger.info("[FRAMEWORK] " + "=" * 80)
    
    # Create reports directory
    os.makedirs('reports', exist_ok=True)
    os.makedirs('reports/junit', exist_ok=True)
    logger.debug("[FILE] Created reports directories")
    
    # Load environment configuration from .env files
    load_environment_config(context)
    
    # Load and log environment configuration
    env_name = os.getenv('ENVIRONMENT', os.getenv('TEST_ENVIRONMENT', 'test'))
    context.base_url = os.getenv('BASE_URL')
    context.auth_token = os.getenv('AUTH_TOKEN', 'banking-api-key-2024')
    context.request_timeout = int(os.getenv('REQUEST_TIMEOUT', '30'))
    context.performance_threshold_ms = int(os.getenv('PERFORMANCE_THRESHOLD_MS', '2000'))
    context.environment = env_name
    
    # Validate that required configuration is present
    if not context.base_url:
        raise ValueError(f"BASE_URL not found in environment {env_name}. Please check your .env file in environments/.env.{env_name}")
    
    logger.info(f"[ENV] Configuration loaded successfully for environment: {env_name}")
    
    # Initialize authentication headers
    context.auth_headers = {
        'Authorization': f'Bearer {context.auth_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Correlation-Id': f'test-{datetime.now().strftime("%Y%m%d%H%M%S")}'
    }
    
    # Log environment details (mask sensitive data)
    logger.info(f"[ENV] Test Environment: {env_name}")
    logger.info(f"[URL] API Base URL: {context.base_url}")
    logger.info(f"[AUTH] Auth Token: {'*' * (len(context.auth_token) - 4) + context.auth_token[-4:]}")
    logger.info(f"[FILE] Log File: {context.log_file}")
    
    # Log system information
    logger.info(f"[PLATFORM]  Platform: {os.name}")
    logger.info(f"[TIME] Start Time: {datetime.now().isoformat()}")
    logger.info(f"[USER] User: {os.getenv('USER', os.getenv('USERNAME', 'unknown'))}")
    logger.info(f"[DIR] Working Directory: {os.getcwd()}")
    logger.info(f"[TIMEOUT] Request Timeout: {context.request_timeout}s")
    logger.info(f"[PERFORMANCE] Performance Threshold: {context.performance_threshold_ms}ms")
    
    # Initialize test metrics
    context.test_metrics = {
        'start_time': datetime.now(),
        'total_scenarios': 0,
        'passed_scenarios': 0,
        'failed_scenarios': 0,
        'skipped_scenarios': 0,
        'api_calls': 0,
        'total_response_time': 0.0
    }
    
    logger.info("[START] Framework initialization complete - Ready to execute tests")


def before_scenario(context, scenario):
    """Hook that runs before each scenario."""
    scenario_start_time = datetime.now()
    context.scenario_start_time = scenario_start_time
    
    # Remove step reloading logic that might be interfering with Behave
    pass
    
    # Log scenario start with detailed information
    context.logger.info("[SCENARIO] " + "=" * 60)
    context.logger.info(f"[TEST] SCENARIO START: {scenario.name}")
    context.logger.info(f"[FILE] Feature: {scenario.feature.name}")
    context.logger.info(f"[LOCATION] Location: {scenario.location}")
    context.logger.info(f"[TAGS]  Tags: {', '.join(scenario.tags) if scenario.tags else 'None'}")
    context.logger.info(f"[TIME] Start Time: {scenario_start_time.isoformat()}")
    context.logger.info("[SCENARIO] " + "=" * 60)
    
    # Initialize scenario-level metrics
    context.scenario_metrics = {
        'start_time': scenario_start_time,
        'api_calls': 0,
        'total_response_time': 0.0,
        'errors': []
    }
    
    # Update total scenario count
    context.test_metrics['total_scenarios'] += 1


def after_scenario(context, scenario):
    """Hook that runs after each scenario."""
    scenario_end_time = datetime.now()
    scenario_duration = scenario_end_time - context.scenario_start_time
    
    # Determine scenario status
    status = "[PASSED] PASSED" if scenario.status == 'passed' else "[FAILED] FAILED"
    status_emoji = "[PASSED]" if scenario.status == 'passed' else "[FAILED]"
    
    # Update test metrics
    if scenario.status == 'passed':
        context.test_metrics['passed_scenarios'] += 1
    elif scenario.status == 'failed':
        context.test_metrics['failed_scenarios'] += 1
        # Capture failure details immediately
        capture_failure_details(context, scenario, scenario_end_time, scenario_duration)
    else:
        context.test_metrics['skipped_scenarios'] += 1
    
    # Log scenario completion with detailed metrics
    context.logger.info("[END] " + "=" * 60)
    context.logger.info(f"{status_emoji} SCENARIO COMPLETE: {scenario.name}")
    context.logger.info(f"[INFO] Status: {status}")
    context.logger.info(f"[TIME]  Duration: {scenario_duration}")
    context.logger.info(f"[URL] API Calls Made: {context.scenario_metrics.get('api_calls', 0)}")
    
    if context.scenario_metrics.get('total_response_time', 0) > 0:
        avg_response_time = context.scenario_metrics['total_response_time'] / max(context.scenario_metrics['api_calls'], 1)
        context.logger.info(f"[PERFORMANCE] Avg Response Time: {avg_response_time:.3f}s")
        context.logger.info(f"[INFO] Total Response Time: {context.scenario_metrics['total_response_time']:.3f}s")
    
    # Log any errors that occurred
    if hasattr(context, 'last_error') and context.last_error:
        context.logger.error(f"[ERROR] Last Error: {context.last_error}")
    
    # Log final API response details if available
    if hasattr(context, 'response') and context.response:
        context.logger.info(f"[URL] Final Response Status: {context.response.status_code}")
        if hasattr(context.response, 'headers'):
            correlation_id = context.response.headers.get('X-Correlation-Id', 'Not Found')
            context.logger.info(f"[VERIFY] Correlation ID: {correlation_id}")
    
    context.logger.info("[END] " + "=" * 60)
    
    # Clear scenario-specific data
    if hasattr(context, 'scenario_metrics'):
        delattr(context, 'scenario_metrics')
    if hasattr(context, 'last_error'):
        delattr(context, 'last_error')


def after_all(context):
    """Hook that runs after all tests."""
    end_time = datetime.now()
    total_duration = end_time - context.test_metrics['start_time']
    
    # Calculate final metrics
    total_scenarios = context.test_metrics['total_scenarios']
    passed = context.test_metrics['passed_scenarios']
    failed = context.test_metrics['failed_scenarios']
    skipped = context.test_metrics['skipped_scenarios']
    
    pass_rate = (passed / total_scenarios * 100) if total_scenarios > 0 else 0
    
    # Log comprehensive test summary
    context.logger.info("[RESULTS] " + "=" * 80)
    context.logger.info("[FRAMEWORK] BANKING API BDD TEST FRAMEWORK - EXECUTION COMPLETE")
    context.logger.info("[RESULTS] " + "=" * 80)
    context.logger.info(f"[TIMEOUT] Total Execution Time: {total_duration}")
    context.logger.info(f"[INFO] Total Scenarios: {total_scenarios}")
    context.logger.info(f"[PASSED] Passed: {passed}")
    context.logger.info(f"[FAILED] Failed: {failed}")
    context.logger.info(f"[SKIPPED]  Skipped: {skipped}")
    context.logger.info(f"[PERFORMANCE] Pass Rate: {pass_rate:.2f}%")
    context.logger.info(f"[URL] Total API Calls: {context.test_metrics['api_calls']}")
    
    if context.test_metrics['total_response_time'] > 0:
        avg_response_time = context.test_metrics['total_response_time'] / max(context.test_metrics['api_calls'], 1)
        context.logger.info(f"[PERFORMANCE] Average Response Time: {avg_response_time:.3f}s")
        context.logger.info(f"[INFO] Total Response Time: {context.test_metrics['total_response_time']:.3f}s")
    
    context.logger.info(f"[FILE] Detailed Logs: {context.log_file}")
    context.logger.info(f"[TIME] End Time: {end_time.isoformat()}")
    
    # Create failure summary file if there were failures
    if failed > 0 and hasattr(context, 'failure_files') and context.failure_files:
        create_failure_summary(context, end_time, failed)
    
    # Log recommendations based on results
    if pass_rate == 100:
        context.logger.info("[SUCCESS] ALL TESTS PASSED! Great job!")
    elif pass_rate >= 90:
        context.logger.info("[GOOD] HIGH SUCCESS RATE! Minor issues to address.")
    elif pass_rate >= 70:
        context.logger.warning("[WARNING]  MODERATE SUCCESS RATE. Review failed tests.")
    else:
        context.logger.error("[ERROR] LOW SUCCESS RATE. Significant issues need attention.")
    
    # Log failure file locations if any
    if hasattr(context, 'failure_files') and context.failure_files:
        context.logger.error("[HEADERS] FAILURE DETAILS AVAILABLE IN:")
        for failure_file in context.failure_files:
            context.logger.error(f"   [BODY] {failure_file}")
        context.logger.error(f"   [BODY] logs/failures/FAILURE_SUMMARY_{end_time.strftime('%Y%m%d_%H%M%S')}.txt")
    
    context.logger.info("[RESULTS] " + "=" * 80)