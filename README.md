# Coding_team

## Overview

The Coding_team repository is a comprehensive AI-powered software development framework featuring 10 specialized AI agents that collaborate to manage and execute software development projects. This system automates various aspects of software development including project management, architecture design, frontend/backend development, data engineering, ML operations, DevOps, quality assurance, and security.

## Project Purpose

This framework provides:
- **Automated AI Agents**: 10 specialized agents handling different aspects of software development
- **Helper Utilities**: Reusable scripts for common development tasks
- **Development Tools**: Code formatting, testing, logging, and analysis utilities
- **Project Management**: Built-in tools for tracking tasks, managing resources, and analyzing risks

## Repository Structure

```
Coding_team/
├── Agents/              # AI Agent implementations
│   ├── A1_Project_Manager/
│   ├── A2_Software_Architect/
│   ├── A3_Frontend_Developer/
│   ├── A4_Backend_Developer/
│   ├── A5_Data_Engineer/
│   ├── A6_Data_Scientist/
│   ├── A7_Machine_Learning_Engineer/
│   ├── A8_DevOps_Engineer/
│   ├── A9_Quality_Assurance_Engineer/
│   └── A10_Security_Engineer/
├── helpers/             # Utility scripts for common operations
│   ├── DtO.py          # Datetime operations
│   ├── FaDO.py         # File and directory operations
│   ├── StrO.py         # String operations
│   ├── log_analysis.py # Log file analysis
│   ├── unit_test_runner.py # Test execution
│   └── ...
├── docs/               # Documentation and project tracking
├── audits/             # Code audit reports and analysis
├── my_library/         # Core library modules
└── README.md           # This file
```

## AI Agents

The system includes 10 specialized AI agents:

1. **Project Manager** (A1) - Oversees projects, sets goals, manages timelines
2. **Software Architect** (A2) - Designs system architecture, analyzes code quality
3. **Frontend Developer** (A3) - Handles UI/UX development and testing
4. **Backend Developer** (A4) - Manages server-side logic and databases
5. **Data Engineer** (A5) - Implements data pipelines and validation
6. **Data Scientist** (A6) - Creates models and visualizations
7. **Machine Learning Engineer** (A7) - Deploys and optimizes ML models
8. **DevOps Engineer** (A8) - Manages deployment and monitoring
9. **Quality Assurance Engineer** (A9) - Creates and executes test plans
10. **Security Engineer** (A10) - Performs security assessments and improvements

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/KHMSmartBuild/Coding_team.git
cd Coding_team
```

2. Create and activate a virtual environment:
```bash
python3 -m venv coding_team_venv
source coding_team_venv/bin/activate  # On Windows: coding_team_venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt  # If requirements.txt exists
```

## Usage

### Using Helper Utilities

The `helpers/` directory contains utility scripts for common operations:

**Datetime Operations:**
```python
from helpers.DtO import parse_datetime, format_datetime, time_since

# Parse datetime string
dt = parse_datetime("2024-01-15 10:30:00")

# Format datetime
formatted = format_datetime(dt, "%Y-%m-%d")

# Calculate time since
elapsed = time_since(dt)
```

**File Operations:**
```python
from helpers.FaDO import create_directory, delete_directory

# Create a new directory
create_directory("./my_new_folder")

# Delete a directory
delete_directory("./old_folder")
```

**String Operations:**
```python
from helpers.StrO import to_snake_case, to_camel_case

# Convert to snake_case
snake = to_snake_case("MyVariableName")  # Returns: "my_variable_name"

# Convert to camelCase
camel = to_camel_case("my_variable_name")  # Returns: "myVariableName"
```

### Log Analysis

Analyze log files using the built-in log analysis tool:

```bash
python helpers/log_analysis.py /path/to/logfile.log
```

### Running Tests

Execute unit tests using the test runner:

```bash
python helpers/unit_test_runner.py
```

## Helper Scripts Overview

The `helpers/` directory provides utilities for:

- **api_testing.py** - API endpoint testing utilities
- **backup_restore.py** - Backup and restore operations
- **code_documentation.py** - Generate code documentation
- **code_formatting_and_linting.py** - Code quality tools
- **database_migration.py** - Database migration management
- **environment_setup.py** - Development environment setup
- **log_analysis.py** - Log file parsing and analysis
- **performance_profiling.py** - Code performance profiling
- **unit_test_runner.py** - Automated test execution

## Logging

The project uses Python's standard logging module. Logs follow the format:

```
YYYY-MM-DD HH:MM:SS - LEVEL - Message
```

Log levels used:
- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages for potentially harmful situations
- **ERROR**: Error messages for serious problems
- **CRITICAL**: Critical issues requiring immediate attention

See the [Logging Guide](docs/LOGGING.md) for detailed logging configuration and usage.

## Testing

The project uses pytest for testing. Test files are organized by module:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_helpers.py

# Run with coverage
pytest --cov=. --cov-report=html
```

See [Testing Guide](docs/TESTING.md) for more information on writing and running tests.

## Audits

The `audits/` directory contains automated code audit reports. To generate a new audit:

```bash
python audits/generate_audit_report.py
```

This creates timestamped reports with:
- Repository structure analysis
- Script completeness metrics
- TODO tracking
- Placeholder identification
- Documentation coverage
- Test coverage analysis

See [audits/README.md](audits/README.md) for detailed information about audit reports.

## Contributing

When contributing to this repository:

1. Create a feature branch from `main`
2. Make your changes following the existing code style
3. Add tests for new functionality
4. Update documentation as needed
5. Ensure all tests pass
6. Submit a pull request with a clear description

## Development Status

Current repository metrics (from latest audit):
- **Total Files**: 81
- **Python Files**: 69
- **Average Completeness**: 43.2/100
- **TODO Items**: 54
- **Placeholders**: 146

See `audits/AUDIT_REPORT_*.md` for detailed analysis.

## License

[Specify license information]

## Contact

For questions or issues, please open an issue on GitHub or contact the repository maintainers.

## Acknowledgments

This project uses various open-source libraries and tools. Special thanks to:
- LangChain for AI agent framework
- OpenAI for language models
- The Python community for excellent tools and libraries