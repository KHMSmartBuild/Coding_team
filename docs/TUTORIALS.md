# Coding_team Tutorials

This document provides step-by-step tutorials for using the Coding_team framework.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Using Helper Utilities](#using-helper-utilities)
3. [Working with AI Agents](#working-with-ai-agents)
4. [Log Analysis](#log-analysis)
5. [Testing Your Code](#testing-your-code)
6. [Running Code Audits](#running-code-audits)

## Getting Started

### Tutorial 1: Setting Up Your Development Environment

**Objective**: Set up a working development environment for the Coding_team project.

**Prerequisites**:
- Python 3.8 or higher installed
- Git installed
- Basic command line knowledge

**Steps**:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/KHMSmartBuild/Coding_team.git
   cd Coding_team
   ```

2. **Create a virtual environment**:
   ```bash
   # On Linux/Mac
   python3 -m venv coding_team_venv
   source coding_team_venv/bin/activate
   
   # On Windows
   python -m venv coding_team_venv
   coding_team_venv\Scripts\activate
   ```

3. **Verify installation**:
   ```bash
   python --version  # Should show Python 3.8 or higher
   which python      # Should point to your virtual environment
   ```

4. **Explore the project structure**:
   ```bash
   ls -la            # List all directories
   tree -L 2         # View directory tree (if tree is installed)
   ```

**Expected Outcome**: You have a working Python environment ready for development.

---

## Using Helper Utilities

### Tutorial 2: Working with Datetime Operations

**Objective**: Learn to use the DtO.py module for datetime operations.

**Steps**:

1. **Create a test script** (`test_datetime.py`):
   ```python
   from helpers.DtO import parse_datetime, format_datetime, time_since
   from datetime import datetime
   
   # Parse a datetime string
   date_string = "2024-01-15 14:30:00"
   dt = parse_datetime(date_string)
   print(f"Parsed datetime: {dt}")
   
   # Format datetime in different ways
   formatted_date = format_datetime(dt, "%B %d, %Y")
   print(f"Formatted: {formatted_date}")
   
   # Calculate time elapsed
   elapsed = time_since(dt, datetime.now())
   print(f"Time since: {elapsed}")
   ```

2. **Run the script**:
   ```bash
   python test_datetime.py
   ```

**Expected Output**:
```
Parsed datetime: 2024-01-15 14:30:00
Formatted: January 15, 2024
Time since: X days, Y:Z:W
```

---

### Tutorial 3: File and Directory Operations

**Objective**: Use FaDO.py to manage files and directories.

**Steps**:

1. **Create a test script** (`test_file_ops.py`):
   ```python
   from helpers.FaDO import create_directory, delete_directory
   
   # Create a test directory
   test_dir = "./test_directory"
   create_directory(test_dir)
   
   # Create a nested directory
   nested_dir = "./test_directory/nested/deep"
   create_directory(nested_dir)
   
   # Clean up (uncomment when ready)
   # delete_directory(test_dir)
   ```

2. **Run the script**:
   ```bash
   python test_file_ops.py
   ```

3. **Verify directories were created**:
   ```bash
   ls -la test_directory/
   ```

**Safety Tip**: Always verify paths before deleting directories to avoid data loss.

---

### Tutorial 4: String Manipulation

**Objective**: Use StrO.py for string case conversions.

**Steps**:

1. **Create a test script** (`test_strings.py`):
   ```python
   from helpers.StrO import to_snake_case, to_camel_case, clean_string
   
   # Test different conversions
   original = "MyVariableName"
   
   snake = to_snake_case(original)
   print(f"Snake case: {snake}")
   
   camel = to_camel_case("my_variable_name")
   print(f"Camel case: {camel}")
   
   # Clean a string with special characters
   dirty_string = "Hello, World! @#$%"
   clean = clean_string(dirty_string)
   print(f"Cleaned: {clean}")
   ```

2. **Run and observe output**:
   ```bash
   python test_strings.py
   ```

**Expected Output**:
```
Snake case: my_variable_name
Camel case: myVariableName
Cleaned: Hello  World     
```

---

## Working with AI Agents

### Tutorial 5: Understanding the Agent System

**Objective**: Learn about the AI agent architecture.

**Agent Overview**:

Each agent in the `Agents/` directory has a specific role:

```
A1_Project_Manager/
├── Agent_Project_Manager.py    # Main agent implementation
├── Change_Management.py         # Change management functionality
├── Resource_Allocation.py       # Resource allocation logic
├── Risk_Analysis.py            # Risk assessment tools
├── Team_Collaboration.py       # Team collaboration features
└── make_a_decision.py          # Decision-making utilities
```

**Example: Using the Project Manager Agent**:

```python
from Agents.A1_Project_Manager.Agent_Project_Manager import project_manager

# Define agent tasks
agent_tasks = {
    'Agent_1': {'task': 'Code documentation', 'status': 'Pending'},
    'Agent_2': {'task': 'Code review', 'status': 'Pending'},
    'Agent_3': {'task': 'Testing', 'status': 'Pending'},
}

# Run project manager
result = project_manager(agent_tasks)
if result:
    print("Project management completed successfully")
```

**Note**: Some agent functionality requires API keys (OpenAI, etc.). Set these in environment variables before running.

---

## Log Analysis

### Tutorial 6: Analyzing Log Files

**Objective**: Use log_analysis.py to parse and analyze application logs.

**Steps**:

1. **Create a sample log file** (`sample.log`):
   ```
   2024-01-15 10:00:00 - INFO - Application started
   2024-01-15 10:01:00 - DEBUG - Processing user request
   2024-01-15 10:02:00 - WARNING - Slow database query detected
   2024-01-15 10:03:00 - ERROR - Connection timeout
   2024-01-15 10:04:00 - INFO - Request completed
   ```

2. **Run the log analyzer**:
   ```bash
   python helpers/log_analysis.py sample.log
   ```

**Expected Output**:
```
INFO: 2 entries
  2024-01-15 10:00:00 - Application started
  2024-01-15 10:04:00 - Request completed
DEBUG: 1 entries
  2024-01-15 10:01:00 - Processing user request
WARNING: 1 entries
  2024-01-15 10:02:00 - Slow database query detected
ERROR: 1 entries
  2024-01-15 10:03:00 - Connection timeout
```

**Advanced Usage**:

You can modify `log_analysis.py` to:
- Filter by date range
- Count error occurrences
- Generate visualization charts
- Export reports to CSV

---

## Testing Your Code

### Tutorial 7: Running Unit Tests

**Objective**: Execute unit tests using the test runner.

**Steps**:

1. **Understand the test runner**:
   The `helpers/unit_test_runner.py` script uses pytest to run tests.

2. **Run tests** (if tests exist):
   ```bash
   python helpers/unit_test_runner.py
   ```

3. **Create a simple test** (`test_example.py`):
   ```python
   def test_addition():
       assert 1 + 1 == 2
   
   def test_string_upper():
       assert "hello".upper() == "HELLO"
   
   def test_list_append():
       my_list = [1, 2, 3]
       my_list.append(4)
       assert my_list == [1, 2, 3, 4]
   ```

4. **Run with pytest directly**:
   ```bash
   pytest test_example.py -v
   ```

**Expected Output**:
```
test_example.py::test_addition PASSED
test_example.py::test_string_upper PASSED
test_example.py::test_list_append PASSED
```

---

## Running Code Audits

### Tutorial 8: Generating an Audit Report

**Objective**: Create a comprehensive code audit of the repository.

**Steps**:

1. **Run the audit script**:
   ```bash
   python audits/generate_audit_report.py
   ```

2. **Wait for completion**:
   The script will analyze all Python files and generate reports. This may take a minute.

3. **Review generated files**:
   ```bash
   ls -lah audits/
   ```

   You should see new timestamped files:
   - `AUDIT_REPORT_[timestamp].md` - Main report
   - `file_tree_[timestamp].csv` - File structure
   - `scripts_analysis_[timestamp].csv` - Script details
   - `todos_[timestamp].csv` - TODO items
   - `placeholders_[timestamp].csv` - Placeholders
   - `completeness_[timestamp].csv` - Completeness scores

4. **Open the main report**:
   ```bash
   cat audits/AUDIT_REPORT_*.md | less
   # or open in your text editor
   ```

5. **Analyze specific metrics**:
   ```bash
   # View completeness scores
   cat audits/completeness_*.csv | column -t -s,
   
   # Count TODO items
   wc -l audits/todos_*.csv
   
   # View placeholders
   cat audits/placeholders_*.csv
   ```

**What to Look For**:
- Scripts with low completeness scores (< 50)
- High number of TODOs in specific files
- Placeholder implementations that need real code
- Missing documentation or tests

---

## Best Practices

### Coding Standards

1. **Always use type hints**:
   ```python
   def process_data(input_data: str) -> dict:
       return {"result": input_data}
   ```

2. **Include docstrings**:
   ```python
   def calculate_total(items: list) -> float:
       """
       Calculate the total sum of item prices.
       
       Args:
           items: List of item dictionaries with 'price' key
           
       Returns:
           Total sum as a float
       """
       return sum(item['price'] for item in items)
   ```

3. **Use logging instead of print**:
   ```python
   import logging
   
   logging.info("Processing started")
   # Instead of: print("Processing started")
   ```

### Testing Guidelines

1. **Test edge cases**:
   ```python
   def test_empty_list():
       assert process_list([]) == []
   
   def test_none_input():
       with pytest.raises(ValueError):
           process_data(None)
   ```

2. **Use descriptive test names**:
   ```python
   def test_user_authentication_with_valid_credentials():
       # Test implementation
       pass
   ```

3. **Keep tests independent**:
   Each test should be able to run in isolation.

---

## Troubleshooting

### Common Issues

**Issue**: Import errors when running scripts
**Solution**: Ensure you're in the project root directory and virtual environment is activated

**Issue**: Missing dependencies
**Solution**: Install required packages (check script imports for requirements)

**Issue**: Permission errors with file operations
**Solution**: Check file permissions and ensure you have write access

**Issue**: Log analysis shows no output
**Solution**: Verify log file format matches the expected pattern in `log_analysis.py`

---

## Next Steps

After completing these tutorials:

1. Explore individual agent implementations in `Agents/`
2. Review the audit reports to understand code quality
3. Contribute by addressing TODO items
4. Add tests for untested functionality
5. Improve documentation where needed

For more detailed information, refer to:
- [README.md](../README.md) - Project overview
- [audits/README.md](../audits/README.md) - Audit documentation
- [LOGGING.md](LOGGING.md) - Logging configuration
- [TESTING.md](TESTING.md) - Testing guide

---

**Questions or Issues?**
Open an issue on GitHub or refer to the main documentation.
