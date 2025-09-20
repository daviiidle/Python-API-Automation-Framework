"""
Behave environment configuration and hooks for Banking API BDD tests.
This file contains before/after hooks for different test lifecycle events.
"""

import os
import logging
from datetime import datetime
from typing import Any, Dict

from dotenv import load_dotenv
from behave import fixture, use_fixture
from behave.runner import Context

from support.config.config_manager import ConfigManager
from support.clients.api_client import APIClient
from support.utils.logger import setup_logger


def load_environment_config(env_name: str = None) -> None:
    """Load environment configuration based on environment name."""
    if not env_name:
        env_name = os.getenv('TEST_ENVIRONMENT', 'test')
    
    env_file_path = f"environments/.env.{env_name}"
    if os.path.exists(env_file_path):
        load_dotenv(env_file_path)
        print(f"Loaded environment configuration from {env_file_path}")
    else:
        print(f"Warning: Environment file {env_file_path} not found")


@fixture
def api_client_fixture(context: Context) -> APIClient:
    """Create and configure API client for tests."""
    config = ConfigManager()
    client = APIClient(
        base_url=config.base_url,
        auth_token=config.auth_token,
        timeout=config.request_timeout,
        retry_count=config.retry_count
    )
    return client


def before_all(context: Context) -> None:
    """
    Hook that runs before all tests.
    Initialize global test configuration and logging.
    """
    # Load environment configuration
    env_name = context.config.userdata.get('environment', 'test')
    load_environment_config(env_name)
    
    # Setup logging
    context.logger = setup_logger('banking_api_tests')
    context.logger.info("=" * 80)
    context.logger.info(f"Starting Banking API BDD Test Suite - Environment: {env_name}")
    context.logger.info("=" * 80)
    
    # Initialize configuration manager
    context.config_manager = ConfigManager()
    
    # Create reports directory
    os.makedirs('reports', exist_ok=True)
    
    # Test execution metadata
    context.test_start_time = datetime.now()
    context.test_results = {
        'total_scenarios': 0,
        'passed_scenarios': 0,
        'failed_scenarios': 0,
        'skipped_scenarios': 0
    }
    
    # Performance tracking
    context.performance_metrics = []


def before_feature(context: Context, feature) -> None:
    """
    Hook that runs before each feature file.
    Initialize feature-specific setup.
    """
    context.logger.info(f"Starting Feature: {feature.name}")
    context.feature_start_time = datetime.now()
    
    # Tag-based setup
    if 'api' in feature.tags:
        use_fixture(api_client_fixture, context)
        context.logger.info("API client initialized for feature")
    
    if 'performance' in feature.tags:
        context.performance_test_mode = True
        context.logger.info("Performance testing mode enabled")
    else:
        context.performance_test_mode = False


def before_scenario(context: Context, scenario) -> None:
    """
    Hook that runs before each scenario.
    Initialize scenario-specific setup and logging.
    """
    context.logger.info(f"Starting Scenario: {scenario.name}")
    context.scenario_start_time = datetime.now()
    context.scenario_data = {}
    
    # Initialize API client if not already done
    if not hasattr(context, 'api_client'):
        context.api_client = use_fixture(api_client_fixture, context)
    
    # Reset API client session for each scenario
    context.api_client.reset_session()
    
    # Generate correlation ID for tracking
    context.correlation_id = f"test-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{hash(scenario.name) & 0x7FFFFFFF}"
    context.api_client.set_correlation_id(context.correlation_id)
    
    # Tag-based scenario setup
    if 'smoke' in scenario.tags:
        context.logger.info("Running smoke test scenario")
    
    if 'data_validation' in scenario.tags:
        context.validate_response_schema = True
    else:
        context.validate_response_schema = False
    
    # Performance testing setup
    if 'performance' in scenario.tags or context.performance_test_mode:
        context.performance_thresholds = {
            'response_time_ms': int(os.getenv('PERFORMANCE_THRESHOLD_MS', 2000))
        }


def after_scenario(context: Context, scenario) -> None:
    """
    Hook that runs after each scenario.
    Cleanup and result logging.
    """
    scenario_duration = datetime.now() - context.scenario_start_time
    
    # Update test results
    context.test_results['total_scenarios'] += 1
    if scenario.status == 'passed':
        context.test_results['passed_scenarios'] += 1
        context.logger.info(f"✓ Scenario PASSED: {scenario.name} (Duration: {scenario_duration})")
    elif scenario.status == 'failed':
        context.test_results['failed_scenarios'] += 1
        context.logger.error(f"✗ Scenario FAILED: {scenario.name} (Duration: {scenario_duration})")
        
        # Log failure details
        if hasattr(context, 'api_client') and context.api_client.last_response:
            context.logger.error(f"Last API Response Status: {context.api_client.last_response.status_code}")
            context.logger.error(f"Last API Response: {context.api_client.last_response.text[:500]}...")
    else:
        context.test_results['skipped_scenarios'] += 1
        context.logger.warning(f"⚠ Scenario SKIPPED: {scenario.name}")
    
    # Performance metrics collection
    if hasattr(context, 'api_client') and context.api_client.last_response_time:
        metric = {
            'scenario': scenario.name,
            'response_time_ms': context.api_client.last_response_time * 1000,
            'timestamp': context.scenario_start_time.isoformat(),
            'status': scenario.status
        }
        context.performance_metrics.append(metric)
    
    # Cleanup scenario data
    if hasattr(context, 'scenario_data'):
        del context.scenario_data


def after_feature(context: Context, feature) -> None:
    """
    Hook that runs after each feature file.
    Feature-level cleanup and reporting.
    """
    feature_duration = datetime.now() - context.feature_start_time
    context.logger.info(f"Completed Feature: {feature.name} (Duration: {feature_duration})")
    
    # Feature-specific cleanup
    if hasattr(context, 'api_client'):
        context.api_client.close_session()


def after_all(context: Context) -> None:
    """
    Hook that runs after all tests.
    Final cleanup and test summary reporting.
    """
    total_duration = datetime.now() - context.test_start_time
    
    # Test execution summary
    context.logger.info("=" * 80)
    context.logger.info("TEST EXECUTION SUMMARY")
    context.logger.info("=" * 80)
    context.logger.info(f"Total Duration: {total_duration}")
    context.logger.info(f"Total Scenarios: {context.test_results['total_scenarios']}")
    context.logger.info(f"Passed: {context.test_results['passed_scenarios']}")
    context.logger.info(f"Failed: {context.test_results['failed_scenarios']}")
    context.logger.info(f"Skipped: {context.test_results['skipped_scenarios']}")
    
    # Calculate pass rate
    if context.test_results['total_scenarios'] > 0:
        pass_rate = (context.test_results['passed_scenarios'] / context.test_results['total_scenarios']) * 100
        context.logger.info(f"Pass Rate: {pass_rate:.2f}%")
    
    # Performance metrics summary
    if context.performance_metrics:
        avg_response_time = sum(m['response_time_ms'] for m in context.performance_metrics) / len(context.performance_metrics)
        max_response_time = max(m['response_time_ms'] for m in context.performance_metrics)
        context.logger.info(f"Average Response Time: {avg_response_time:.2f}ms")
        context.logger.info(f"Max Response Time: {max_response_time:.2f}ms")
        
        # Save performance metrics to file
        import json
        metrics_file = f"reports/performance_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(metrics_file, 'w') as f:
            json.dump(context.performance_metrics, f, indent=2)
        context.logger.info(f"Performance metrics saved to: {metrics_file}")
    
    context.logger.info("=" * 80)
    context.logger.info("Banking API BDD Test Suite Completed")
    context.logger.info("=" * 80)