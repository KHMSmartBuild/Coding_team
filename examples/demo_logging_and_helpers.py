#!/usr/bin/env python3
"""
Demo script showcasing the Coding_team logging and helper utilities.

This script demonstrates:
- Proper logging setup and usage
- String operations
- Datetime operations

Run with: python examples/demo_logging_and_helpers.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helpers.logging_config import get_logger, log_function_call
from helpers.StrO import to_snake_case, to_camel_case, clean_string
from helpers.DtO import parse_datetime, format_datetime, time_since
from datetime import datetime
import time

# Get a logger for this module
logger = get_logger(__name__)


@log_function_call(logger)
def demonstrate_string_operations():
    """Demonstrate string manipulation utilities."""
    logger.info("=== String Operations Demo ===")
    
    test_strings = [
        "MyVariableName",
        "my-variable-name",
        "my variable name",
        "CONSTANT_VALUE"
    ]
    
    for test_str in test_strings:
        snake = to_snake_case(test_str)
        camel = to_camel_case(test_str)
        logger.info(f"Original: '{test_str}'")
        logger.info(f"  → snake_case: '{snake}'")
        logger.info(f"  → camelCase: '{camel}'")
    
    # Clean string demo
    dirty = "Hello, @World! #2024"
    clean = clean_string(dirty)
    logger.info(f"Cleaned '{dirty}' → '{clean}'")
    
    logger.info("String operations completed successfully\n")


@log_function_call(logger)
def demonstrate_datetime_operations():
    """Demonstrate datetime manipulation utilities."""
    logger.info("=== Datetime Operations Demo ===")
    
    # Parse datetime
    date_str = "2024-01-15 14:30:00"
    parsed = parse_datetime(date_str)
    logger.info(f"Parsed '{date_str}' → {parsed}")
    
    # Format in different ways
    formats = [
        ("%Y-%m-%d", "ISO date"),
        ("%B %d, %Y", "Readable date"),
        ("%I:%M %p", "12-hour time"),
    ]
    
    for fmt, description in formats:
        formatted = format_datetime(parsed, fmt)
        logger.info(f"{description}: {formatted}")
    
    # Calculate time elapsed
    past = datetime(2024, 1, 1, 0, 0, 0)
    now = datetime(2024, 1, 15, 14, 30, 0)
    elapsed = time_since(past, now)
    logger.info(f"Time between 2024-01-01 and 2024-01-15: {elapsed}")
    
    logger.info("Datetime operations completed successfully\n")


@log_function_call(logger)
def demonstrate_logging_levels():
    """Demonstrate different logging levels."""
    logger.info("=== Logging Levels Demo ===")
    
    logger.debug("This is a DEBUG message - detailed diagnostic info")
    logger.info("This is an INFO message - general information")
    logger.warning("This is a WARNING message - something unexpected")
    
    # Simulate an error scenario
    try:
        result = 10 / 0
    except ZeroDivisionError as e:
        logger.error("This is an ERROR message - something failed", exc_info=True)
    
    logger.critical("This is a CRITICAL message - serious problem")
    
    logger.info("Logging levels demonstration completed\n")


def demonstrate_performance_logging():
    """Demonstrate performance logging."""
    logger.info("=== Performance Logging Demo ===")
    
    operations = [
        ("Fast operation", 0.1),
        ("Medium operation", 0.5),
        ("Slow operation", 1.0),
    ]
    
    for operation, duration in operations:
        logger.info(f"Starting: {operation}")
        start_time = datetime.now()
        
        # Simulate work
        time.sleep(duration)
        
        end_time = datetime.now()
        elapsed = time_since(start_time, end_time)
        logger.info(f"Completed: {operation} (took {elapsed})")
    
    logger.info("Performance logging demonstration completed\n")


def main():
    """Main demonstration function."""
    logger.info("="*60)
    logger.info("Coding_team Demo - Logging and Helper Utilities")
    logger.info("="*60)
    logger.info("")
    
    try:
        # Run demonstrations
        demonstrate_string_operations()
        demonstrate_datetime_operations()
        demonstrate_logging_levels()
        demonstrate_performance_logging()
        
        logger.info("="*60)
        logger.info("All demonstrations completed successfully!")
        logger.info("="*60)
        logger.info("")
        logger.info("Check the following for logged output:")
        logger.info("  - Console: Above output")
        logger.info("  - File: logs/app.log (detailed)")
        logger.info("  - File: logs/errors.log (errors only)")
        
    except Exception as e:
        logger.critical(f"Demo failed with error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
