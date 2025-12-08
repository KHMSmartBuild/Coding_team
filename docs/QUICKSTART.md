# Quick Start Guide

Get up and running with the Coding_team project in minutes.

## Prerequisites

- Python 3.8 or higher
- pip package manager
- git

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/KHMSmartBuild/Coding_team.git
cd Coding_team
```

### 2. Set Up Virtual Environment

```bash
# Create virtual environment
python3 -m venv coding_team_venv

# Activate it
# On Linux/Mac:
source coding_team_venv/bin/activate

# On Windows:
coding_team_venv\Scripts\activate
```

### 3. Install Development Dependencies

```bash
pip install -r requirements-dev.txt
```

## Quick Examples

### Using Helper Utilities

#### String Operations
```python
from helpers.StrO import to_snake_case, to_camel_case

# Convert to snake_case
print(to_snake_case("MyVariableName"))  # Output: my_variable_name

# Convert to camelCase
print(to_camel_case("my_variable_name"))  # Output: myVariableName
```

#### Datetime Operations
```python
from helpers.DtO import parse_datetime, format_datetime
from datetime import datetime

# Parse a datetime string
dt = parse_datetime("2024-01-15 14:30:00")

# Format it differently
formatted = format_datetime(dt, "%B %d, %Y")
print(formatted)  # Output: January 15, 2024
```

#### File Operations
```python
from helpers.FaDO import create_directory, delete_directory

# Create a directory
create_directory("./my_new_folder")

# Delete it (be careful!)
delete_directory("./my_new_folder")
```

### Using the Logging System

```python
from helpers.logging_config import get_logger

# Get a logger
logger = get_logger(__name__)

# Use it
logger.info("Application started")
logger.debug("Debug information")
logger.warning("This is a warning")
logger.error("An error occurred")
```

### Analyzing Log Files

```bash
# Basic analysis
python helpers/log_analysis.py /path/to/logfile.log

# With error analysis
python helpers/log_analysis.py /path/to/logfile.log -e

# With timeline analysis
python helpers/log_analysis.py /path/to/logfile.log -t

# Export to JSON
python helpers/log_analysis.py /path/to/logfile.log -j output.json
```

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_helpers/test_stro.py

# Run with coverage
pytest --cov=helpers --cov-report=html
```

## Project Structure

```
Coding_team/
├── Agents/              # 10 specialized AI agents
├── helpers/             # Utility scripts
│   ├── DtO.py          # Datetime operations
│   ├── FaDO.py         # File/directory operations
│   ├── StrO.py         # String operations
│   └── logging_config.py # Logging configuration
├── docs/               # Documentation
│   ├── TUTORIALS.md    # Step-by-step tutorials
│   ├── LOGGING.md      # Logging guide
│   └── TESTING.md      # Testing guide
├── tests/              # Test suite
├── audits/             # Code audit reports
└── README.md           # Main documentation
```

## Next Steps

1. **Read the full documentation**: Check [README.md](../README.md)
2. **Follow tutorials**: See [docs/TUTORIALS.md](TUTORIALS.md)
3. **Run an audit**: `python audits/generate_audit_report.py`
4. **Explore the agents**: Navigate to `Agents/` directory
5. **Write tests**: Add tests for your code in `tests/`

## Common Tasks

### Generate an Audit Report

```bash
python audits/generate_audit_report.py
```

### Format Code (if black is installed)

```bash
black helpers/ Agents/
```

### Run Linters (if flake8 is installed)

```bash
flake8 helpers/ Agents/ --max-line-length=100
```

## Troubleshooting

### Import Errors

If you see import errors related to `langchain` or `openai`, these are optional dependencies for the AI agents. You can:

1. Install them: `pip install langchain openai`
2. Or use only the helper utilities which don't require them

### Permission Errors

If you get permission errors with file operations, ensure:
- You have write permissions in the directory
- You're running from the correct working directory

### Test Failures

If tests fail due to missing dependencies, install development requirements:
```bash
pip install -r requirements-dev.txt
```

## Getting Help

- Check the [README.md](../README.md) for comprehensive documentation
- Review [docs/TUTORIALS.md](TUTORIALS.md) for step-by-step guides
- See [docs/LOGGING.md](LOGGING.md) for logging configuration
- Read [docs/TESTING.md](TESTING.md) for testing guidelines
- Open an issue on GitHub for bugs or questions

## What's Next?

- Explore the helper utilities in `helpers/`
- Read about the AI agents in `Agents/`
- Review the audit reports in `audits/`
- Add your own functionality
- Write tests for your code
- Improve documentation

Happy coding! 🚀
