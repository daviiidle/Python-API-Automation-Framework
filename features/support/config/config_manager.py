"""
Configuration manager for Banking API BDD tests.
Handles environment-specific configuration and settings.
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class ConfigManager:
    """Centralized configuration management for test framework."""
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        self.environment = os.getenv('ENVIRONMENT', 'test')
        self.base_url = os.getenv('BASE_URL', 'https://your-wiremock-app.railway.app')
        self.auth_token = os.getenv('AUTH_TOKEN', 'banking-api-key-2024')
        self.timeout = int(os.getenv('TIMEOUT', '30'))
        self.retry_count = int(os.getenv('RETRY_COUNT', '3'))
        
        # Headers configuration
        self.correlation_id_header = os.getenv('CORRELATION_ID_HEADER', 'X-Correlation-Id')
        self.content_type = os.getenv('CONTENT_TYPE', 'application/json')
        self.auth_header = os.getenv('AUTH_HEADER', 'Authorization')
        self.auth_prefix = os.getenv('AUTH_PREFIX', 'Bearer')
        
        # Test data configuration
        self.test_data_path = os.getenv('TEST_DATA_PATH', 'test_data/test')
        self.generate_dynamic_data = os.getenv('GENERATE_DYNAMIC_DATA', 'true').lower() == 'true'
        self.validate_schemas = os.getenv('VALIDATE_SCHEMAS', 'true').lower() == 'true'
        
        # Reporting configuration
        self.report_path = os.getenv('REPORT_PATH', 'reports')
        self.allure_results_path = os.getenv('ALLURE_RESULTS_PATH', 'reports/allure-results')
        self.screenshot_on_failure = os.getenv('SCREENSHOT_ON_FAILURE', 'true').lower() == 'true'
        self.junit_reports = os.getenv('JUNIT_REPORTS', 'false').lower() == 'true'
        
        # Performance configuration
        self.request_timeout = int(os.getenv('REQUEST_TIMEOUT', '10'))
        self.concurrency_limit = int(os.getenv('CONCURRENCY_LIMIT', '5'))
        self.performance_threshold_ms = int(os.getenv('PERFORMANCE_THRESHOLD_MS', '2000'))
        
        # Debug configuration
        self.debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_requests = os.getenv('LOG_REQUESTS', 'false').lower() == 'true'
        
        # CI/CD specific configuration
        self.parallel_execution = os.getenv('PARALLEL_EXECUTION', 'false').lower() == 'true'
        self.fail_fast = os.getenv('FAIL_FAST', 'false').lower() == 'true'
        self.verbose_output = os.getenv('VERBOSE_OUTPUT', 'false').lower() == 'true'
    
    def get_auth_header(self) -> Dict[str, str]:
        """Get formatted authentication header."""
        return {
            self.auth_header: f"{self.auth_prefix} {self.auth_token}"
        }
    
    def get_default_headers(self) -> Dict[str, str]:
        """Get default headers for API requests."""
        headers = {
            'Content-Type': self.content_type,
            'Accept': self.content_type
        }
        headers.update(self.get_auth_header())
        return headers
    
    def get_api_endpoints(self) -> Dict[str, str]:
        """Get API endpoint configurations."""
        return {
            'accounts': f"{self.base_url}/accounts",
            'customers': f"{self.base_url}/customers", 
            'bookings': f"{self.base_url}/bookings",
            'loans': f"{self.base_url}/loans",
            'term_deposits': f"{self.base_url}/term-deposits"
        }
    
    def is_production_environment(self) -> bool:
        """Check if running in production environment."""
        return self.environment in ['prod', 'production', 'railway']
    
    def is_ci_environment(self) -> bool:
        """Check if running in CI/CD environment."""
        return any([
            os.getenv('CI'),
            os.getenv('GITHUB_ACTIONS'),
            os.getenv('JENKINS_URL'),
            self.environment == 'test'
        ])
    
    def get_test_data_file(self, service: str, scenario: str) -> str:
        """Get test data file path for specific service and scenario."""
        return os.path.join(self.test_data_path, f"{service}_{scenario}.json")
    
    def validate_configuration(self) -> bool:
        """Validate essential configuration parameters."""
        required_configs = [
            ('BASE_URL', self.base_url),
            ('AUTH_TOKEN', self.auth_token)
        ]
        
        for config_name, config_value in required_configs:
            if not config_value:
                raise ValueError(f"Required configuration {config_name} is not set")
        
        return True
    
    def __str__(self) -> str:
        """String representation of configuration (excluding sensitive data)."""
        config_info = f"""
Banking API Test Configuration:
    Environment: {self.environment}
    Base URL: {self.base_url}
    Auth Token: {'*' * (len(self.auth_token) - 4) + self.auth_token[-4:] if self.auth_token else 'Not Set'}
    Timeout: {self.timeout}s
    Request Timeout: {self.request_timeout}s
    Retry Count: {self.retry_count}
    Debug Mode: {self.debug_mode}
    Performance Threshold: {self.performance_threshold_ms}ms
    Validate Schemas: {self.validate_schemas}
    CI Environment: {self.is_ci_environment()}
        """
        return config_info.strip()