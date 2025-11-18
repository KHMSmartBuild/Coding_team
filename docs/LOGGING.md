# Logging Guide

This guide explains how to implement and use logging in the Coding_team project.

## Table of Contents

1. [Overview](#overview)
2. [Logging Configuration](#logging-configuration)
3. [Using Logging in Scripts](#using-logging-in-scripts)
4. [Log Levels](#log-levels)
5. [Log Format](#log-format)
6. [Best Practices](#best-practices)
7. [Log Analysis](#log-analysis)

## Overview

The Coding_team project uses Python's built-in `logging` module to provide comprehensive application logging. Proper logging helps with:

- **Debugging**: Track down issues in development and production
- **Monitoring**: Observe application behavior over time
- **Auditing**: Keep records of important events
- **Performance**: Identify bottlenecks and slow operations

## Logging Configuration

### Basic Setup

Create a logger in any Python script:

```python
import logging

# Configure logging at the module level
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Create a logger for this module
logger = logging.getLogger(__name__)
```

### Advanced Configuration

For more control, use a configuration file or dictionary:

```python
import logging
import logging.config

# Configuration dictionary
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
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
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': 'app.log',
            'mode': 'a'
        }
    },
    'loggers': {
        '': {  # Root logger
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}

# Apply configuration
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
```

### File-Based Logging Configuration

Save the following to `logging.conf`:

```ini
[loggers]
keys=root,agents,helpers

[handlers]
keys=consoleHandler,fileHandler,errorHandler

[formatters]
keys=standardFormatter,detailedFormatter

[logger_root]
level=INFO
handlers=consoleHandler,fileHandler

[logger_agents]
level=DEBUG
handlers=consoleHandler,fileHandler
qualname=agents
propagate=0

[logger_helpers]
level=DEBUG
handlers=consoleHandler,fileHandler
qualname=helpers
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=standardFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=DEBUG
formatter=detailedFormatter
args=('app.log', 'a')

[handler_errorHandler]
class=FileHandler
level=ERROR
formatter=detailedFormatter
args=('errors.log', 'a')

[formatter_standardFormatter]
format=%(asctime)s - %(levelname)s - %(message)s
datefmt=%Y-%m-%d %H:%M:%S

[formatter_detailedFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s
datefmt=%Y-%m-%d %H:%M:%S
```

Load configuration:

```python
import logging.config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)
```

## Using Logging in Scripts

### Basic Usage

```python
import logging

logger = logging.getLogger(__name__)

def process_data(data):
    """Process data with logging."""
    logger.info(f"Starting data processing for {len(data)} items")
    
    try:
        logger.debug(f"Data content: {data}")
        result = perform_operation(data)
        logger.info("Data processing completed successfully")
        return result
    except ValueError as e:
        logger.error(f"Invalid data format: {e}")
        raise
    except Exception as e:
        logger.critical(f"Unexpected error during processing: {e}", exc_info=True)
        raise
```

### Logging in Helper Scripts

Example for `helpers/FaDO.py`:

```python
import os
import shutil
import logging
from pathlib import Path

# Configure logger
logger = logging.getLogger(__name__)

def create_directory(path: str) -> None:
    """
    Create a new directory at the specified path.
    
    :param path: The path of the new directory.
    """
    logger.debug(f"Attempting to create directory: {path}")
    
    try:
        os.makedirs(path)
        logger.info(f"Directory '{path}' created successfully")
    except FileExistsError:
        logger.warning(f"Directory '{path}' already exists")
    except PermissionError as e:
        logger.error(f"Permission denied creating directory '{path}': {e}")
        raise
    except Exception as e:
        logger.critical(f"Unexpected error creating directory '{path}': {e}", exc_info=True)
        raise
```

### Logging in Agent Scripts

Example for an agent:

```python
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class Agent_Project_Manager:
    """Project Manager Agent with logging."""
    
    def __init__(self):
        logger.info("Initializing Project Manager Agent")
        self.tasks = {}
    
    def assign_task(self, task_id: str, task_data: Dict[str, Any]) -> bool:
        """Assign a task with logging."""
        logger.info(f"Assigning task {task_id}")
        logger.debug(f"Task data: {task_data}")
        
        try:
            # Task assignment logic
            self.tasks[task_id] = task_data
            logger.info(f"Task {task_id} assigned successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to assign task {task_id}: {e}", exc_info=True)
            return False
```

## Log Levels

Python logging provides five standard levels:

### DEBUG (10)
**When to use**: Detailed diagnostic information for debugging

```python
logger.debug("Variable x = %s, y = %s", x, y)
logger.debug("Entering function process_data()")
```

**Examples**:
- Variable values
- Function entry/exit points
- Loop iterations
- Detailed state information

### INFO (20)
**When to use**: General informational messages confirming things are working

```python
logger.info("Application started successfully")
logger.info("Processing 150 records")
logger.info("Database connection established")
```

**Examples**:
- Application startup/shutdown
- Configuration loaded
- Process completion
- Milestone achievements

### WARNING (30)
**When to use**: Something unexpected happened, but the application can continue

```python
logger.warning("Disk space is running low: 5% remaining")
logger.warning("API rate limit approaching: 90% used")
logger.warning("Deprecated function called: use new_function() instead")
```

**Examples**:
- Deprecated features used
- Resource constraints
- Recoverable errors
- Missing optional configurations

### ERROR (40)
**When to use**: Serious problem occurred, some functionality may not work

```python
logger.error("Failed to save file: %s", filename)
logger.error("Database query failed", exc_info=True)
```

**Examples**:
- Failed operations
- Caught exceptions
- Data validation failures
- Connection errors

### CRITICAL (50)
**When to use**: Very serious error, application may not be able to continue

```python
logger.critical("Database connection lost - cannot continue")
logger.critical("Out of memory error", exc_info=True)
```

**Examples**:
- System failures
- Security breaches
- Data corruption
- Unrecoverable errors

## Log Format

### Standard Format

```
YYYY-MM-DD HH:MM:SS - LEVEL - Message
```

Example:
```
2024-01-15 14:30:45 - INFO - Application started
2024-01-15 14:30:46 - DEBUG - Loading configuration from config.json
2024-01-15 14:30:47 - WARNING - Configuration file missing optional parameter
2024-01-15 14:30:50 - ERROR - Failed to connect to database
```

### Detailed Format (with context)

```
YYYY-MM-DD HH:MM:SS - ModuleName - LEVEL - filename.py:line - Message
```

Example:
```
2024-01-15 14:30:45 - agents.project_manager - INFO - Agent_Project_Manager.py:23 - Agent initialized
2024-01-15 14:30:46 - helpers.FaDO - DEBUG - FaDO.py:15 - Creating directory: /tmp/output
```

### Custom Format with Function Names

```python
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s() - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
```

Output:
```
2024-01-15 14:30:45 - mymodule - INFO - process_data() - Starting processing
```

## Best Practices

### 1. Use Appropriate Log Levels

```python
# ✓ Good
logger.debug("User authentication check for user_id=%s", user_id)
logger.info("User logged in successfully: %s", username)
logger.warning("Login attempt with invalid credentials from IP: %s", ip)
logger.error("Failed to authenticate user: %s", error)

# ✗ Avoid
logger.info("x = 5, y = 10")  # Too detailed for INFO level
logger.error("User logged in")  # Not actually an error
```

### 2. Use Lazy Formatting

```python
# ✓ Good - formatting only happens if log level is enabled
logger.debug("Processing item %s with value %s", item_id, value)

# ✗ Avoid - string formatting always happens
logger.debug("Processing item {} with value {}".format(item_id, value))
```

### 3. Include Context Information

```python
# ✓ Good - provides context
logger.error("Failed to process order %s for customer %s: %s", 
             order_id, customer_id, error)

# ✗ Avoid - lacks context
logger.error("Processing failed")
```

### 4. Log Exceptions Properly

```python
# ✓ Good - includes stack trace
try:
    risky_operation()
except Exception as e:
    logger.error("Operation failed", exc_info=True)
    # Or use logger.exception() which automatically includes exc_info=True
    # logger.exception("Operation failed")

# ✗ Avoid - loses stack trace
try:
    risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}")
```

### 5. Don't Log Sensitive Information

```python
# ✗ NEVER DO THIS
logger.info("User password: %s", password)
logger.debug("Credit card: %s", credit_card_number)
logger.info("API key: %s", api_key)

# ✓ Good - mask sensitive data
logger.info("User authenticated: %s", username)
logger.debug("Payment processed: card ending in %s", card_last_4)
```

### 6. Use Logger Names Effectively

```python
# ✓ Good - use __name__ for module-specific loggers
logger = logging.getLogger(__name__)

# For specific subsystems
logger = logging.getLogger('agents.project_manager')
logger = logging.getLogger('helpers.database')
```

### 7. Configure Logging Once

```python
# ✓ Good - configure in main entry point
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()

# ✗ Avoid - configuring in libraries/modules
def my_function():
    logging.basicConfig(level=logging.DEBUG)  # Don't do this
```

## Log Analysis

### Using the Log Analysis Tool

The repository includes `helpers/log_analysis.py` for analyzing log files:

```bash
python helpers/log_analysis.py application.log
```

### Analyzing Logs Manually

**Count log levels**:
```bash
grep -c "ERROR" app.log
grep -c "WARNING" app.log
```

**Find all errors from today**:
```bash
grep "$(date +%Y-%m-%d)" app.log | grep "ERROR"
```

**Show last 100 log entries**:
```bash
tail -100 app.log
```

**Follow log in real-time**:
```bash
tail -f app.log
```

**Extract specific time range**:
```bash
sed -n '/2024-01-15 14:00/,/2024-01-15 15:00/p' app.log
```

### Log Rotation

For long-running applications, use rotating file handlers:

```python
import logging
from logging.handlers import RotatingFileHandler

# Rotate when file reaches 10MB, keep 5 backup files
handler = RotatingFileHandler(
    'app.log',
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5
)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### Time-Based Rotation

```python
from logging.handlers import TimedRotatingFileHandler

# Rotate daily at midnight, keep 7 days
handler = TimedRotatingFileHandler(
    'app.log',
    when='midnight',
    interval=1,
    backupCount=7
)
```

## Examples

### Example 1: Helper Script with Logging

```python
# helpers/data_processor.py
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def process_batch(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Process a batch of items with comprehensive logging."""
    logger.info(f"Starting batch processing for {len(items)} items")
    
    results = []
    errors = 0
    
    for i, item in enumerate(items):
        logger.debug(f"Processing item {i+1}/{len(items)}: {item.get('id', 'unknown')}")
        
        try:
            result = process_single_item(item)
            results.append(result)
        except ValueError as e:
            logger.warning(f"Skipping invalid item {i+1}: {e}")
            errors += 1
        except Exception as e:
            logger.error(f"Failed to process item {i+1}", exc_info=True)
            errors += 1
    
    logger.info(f"Batch processing complete: {len(results)} successful, {errors} errors")
    
    if errors > len(items) * 0.5:
        logger.warning(f"High error rate: {errors}/{len(items)} items failed")
    
    return results
```

### Example 2: Agent with Logging

```python
# Agents/A5_Data_Engineer/data_pipeline.py
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class DataPipeline:
    """Data pipeline with comprehensive logging."""
    
    def __init__(self, config: dict):
        logger.info("Initializing Data Pipeline")
        logger.debug(f"Configuration: {config}")
        self.config = config
        self.stats = {'processed': 0, 'errors': 0}
    
    def run(self) -> bool:
        """Execute the data pipeline."""
        logger.info("Starting data pipeline execution")
        
        try:
            self._extract()
            self._transform()
            self._load()
            
            logger.info(f"Pipeline completed successfully. Stats: {self.stats}")
            return True
            
        except Exception as e:
            logger.critical("Pipeline failed", exc_info=True)
            return False
    
    def _extract(self):
        """Extract data from source."""
        logger.info("Extracting data from source")
        # Implementation
        logger.debug(f"Extracted {self.stats['processed']} records")
    
    def _transform(self):
        """Transform extracted data."""
        logger.info("Transforming data")
        # Implementation
    
    def _load(self):
        """Load data to destination."""
        logger.info("Loading data to destination")
        # Implementation
```

## Integration with Existing Code

To add logging to existing scripts:

1. **Import logging at the top**:
   ```python
   import logging
   ```

2. **Create a logger**:
   ```python
   logger = logging.getLogger(__name__)
   ```

3. **Replace print statements**:
   ```python
   # Before
   print("Processing complete")
   
   # After
   logger.info("Processing complete")
   ```

4. **Add error logging to try/except blocks**:
   ```python
   # Before
   try:
       risky_operation()
   except Exception as e:
       print(f"Error: {e}")
   
   # After
   try:
       risky_operation()
   except Exception as e:
       logger.error("Operation failed", exc_info=True)
   ```

---

## Summary

- Use appropriate log levels for different types of messages
- Configure logging once at application entry point
- Use lazy formatting for performance
- Include context in log messages
- Never log sensitive information
- Use exc_info=True for exceptions
- Consider log rotation for production
- Analyze logs regularly using the provided tools

For more information:
- [Python Logging Documentation](https://docs.python.org/3/library/logging.html)
- [Logging Cookbook](https://docs.python.org/3/howto/logging-cookbook.html)
- [TUTORIALS.md](TUTORIALS.md) - Log analysis tutorial
