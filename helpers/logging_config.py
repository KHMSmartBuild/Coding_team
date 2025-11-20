"""
Logging configuration module for the Coding_team project.

This module provides centralized logging configuration that can be imported
and used throughout the project.

Usage:
    from helpers.logging_config import get_logger
    
    logger = get_logger(__name__)
    logger.info("Application started")
"""

import logging
import logging.config
import os
from pathlib import Path
from typing import Optional

# Default log directory
LOG_DIR = Path(__file__).parent.parent / "logs"

# Ensure log directory exists
LOG_DIR.mkdir(exist_ok=True)

# Logging configuration dictionary
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': str(LOG_DIR / 'app.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'encoding': 'utf8'
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'detailed',
            'filename': str(LOG_DIR / 'errors.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 3,
            'encoding': 'utf8'
        }
    },
    'loggers': {
        '': {  # Root logger
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG',
            'propagate': True
        },
        'helpers': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False
        },
        'Agents': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}


def setup_logging(
    log_level: Optional[str] = None,
    log_to_file: bool = True,
    log_to_console: bool = True
) -> None:
    """
    Configure logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to file
        log_to_console: Whether to log to console
    """
    # Apply configuration
    logging.config.dictConfig(LOGGING_CONFIG)
    
    # Override log level if specified
    if log_level:
        level = getattr(logging, log_level.upper(), logging.INFO)
        logging.getLogger().setLevel(level)
    
    # Disable handlers if requested
    root_logger = logging.getLogger()
    
    if not log_to_file:
        for handler in root_logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                root_logger.removeHandler(handler)
    
    if not log_to_console:
        for handler in root_logger.handlers[:]:
            if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                root_logger.removeHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Name for the logger (typically __name__)
        
    Returns:
        Configured logger instance
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Application started")
    """
    # Ensure logging is configured
    if not logging.getLogger().handlers:
        setup_logging()
    
    return logging.getLogger(name)


def log_function_call(logger: logging.Logger):
    """
    Decorator to log function calls.
    
    Args:
        logger: Logger instance to use
        
    Example:
        >>> logger = get_logger(__name__)
        >>> @log_function_call(logger)
        ... def my_function(x, y):
        ...     return x + y
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"{func.__name__} returned {result}")
                return result
            except Exception as e:
                logger.error(f"{func.__name__} raised {type(e).__name__}: {e}", exc_info=True)
                raise
        return wrapper
    return decorator


def set_log_level(level: str) -> None:
    """
    Set the logging level for all loggers.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    logging.getLogger().setLevel(log_level)


# Initialize logging on module import
setup_logging()


if __name__ == '__main__':
    # Demo usage
    logger = get_logger(__name__)
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    
    print(f"\nLog files created in: {LOG_DIR}")
    print(f"Main log: {LOG_DIR / 'app.log'}")
    print(f"Error log: {LOG_DIR / 'errors.log'}")
