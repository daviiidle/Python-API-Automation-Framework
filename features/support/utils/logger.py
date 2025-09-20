"""
Logging utilities for Banking API BDD tests.
Provides centralized logging configuration and management.
"""

import logging
import os
from datetime import datetime
from typing import Optional


def setup_logger(name: str, log_level: str = None, log_file: str = None) -> logging.Logger:
    """
    Setup and configure logger with file and console handlers.
    
    Args:
        name: Logger name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Get log level from environment or use provided value
    if not log_level:
        log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if log_file or os.getenv('LOG_TO_FILE', 'true').lower() == 'true':
        if not log_file:
            # Create logs directory
            os.makedirs('logs', exist_ok=True)
            log_file = f"logs/banking_api_tests_{datetime.now().strftime('%Y%m%d')}.log"
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get existing logger by name."""
    return logging.getLogger(name)