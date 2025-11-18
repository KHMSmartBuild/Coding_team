# Testing Guide

Comprehensive guide to testing in the Coding_team project.

## Table of Contents

1. [Overview](#overview)
2. [Testing Framework](#testing-framework)
3. [Test Structure](#test-structure)
4. [Writing Tests](#writing-tests)
5. [Running Tests](#running-tests)
6. [Test Coverage](#test-coverage)
7. [Best Practices](#best-practices)
8. [Examples](#examples)

## Overview

Testing ensures code quality, reliability, and maintainability. The Coding_team project uses pytest as the primary testing framework.

### Why Test?

- **Catch bugs early** before they reach production
- **Document behavior** through test cases
- **Enable refactoring** with confidence
- **Improve code design** through testability
- **Reduce debugging time** with clear test failures

## Testing Framework

### Pytest

Pytest is the recommended testing framework for this project.

**Installation**:
```bash
pip install pytest pytest-cov
```

**Key Features**:
- Simple, readable test syntax
- Powerful fixtures for setup/teardown
- Detailed assertion introspection
- Plugin ecosystem
- Coverage reporting

## Test Structure

### Directory Organization

```
Coding_team/
├── tests/                    # Test directory
│   ├── __init__.py
│   ├── test_helpers/         # Tests for helper modules
│   │   ├── test_dto.py
│   │   ├── test_fado.py
│   │   └── test_stro.py
│   ├── test_agents/          # Tests for AI agents
│   │   ├── test_project_manager.py
│   │   └── test_software_architect.py
│   └── conftest.py           # Shared fixtures
├── helpers/                  # Source code
│   ├── DtO.py
│   ├── FaDO.py
│   └── StrO.py
└── Agents/                   # Source code
    └── ...
```

### Test File Naming

- Test files: `test_*.py` or `*_test.py`
- Test functions: `test_*`
- Test classes: `Test*`

## Writing Tests

### Basic Test Structure

```python
# tests/test_example.py

def test_addition():
    """Test basic addition."""
    result = 1 + 1
    assert result == 2

def test_string_concatenation():
    """Test string concatenation."""
    result = "Hello" + " " + "World"
    assert result == "Hello World"
```

### Testing Helper Functions

**Example: Testing String Operations**

```python
# tests/test_helpers/test_stro.py

from helpers.StrO import to_snake_case, to_camel_case, clean_string

class TestStringOperations:
    """Test string operation utilities."""
    
    def test_to_snake_case_simple(self):
        """Test simple camelCase to snake_case conversion."""
        assert to_snake_case("MyVariableName") == "my_variable_name"
    
    def test_to_snake_case_with_spaces(self):
        """Test conversion with spaces."""
        assert to_snake_case("My Variable Name") == "my_variable_name"
    
    def test_to_snake_case_already_snake(self):
        """Test already snake_case string."""
        assert to_snake_case("my_variable_name") == "my_variable_name"
    
    def test_to_camel_case_simple(self):
        """Test snake_case to camelCase conversion."""
        assert to_camel_case("my_variable_name") == "myVariableName"
    
    def test_to_camel_case_with_spaces(self):
        """Test conversion with spaces."""
        assert to_camel_case("my variable name") == "myVariableName"
    
    def test_clean_string_removes_special_chars(self):
        """Test cleaning of special characters."""
        result = clean_string("Hello, World!")
        assert "," not in result
        assert "!" not in result
```

**Example: Testing Datetime Operations**

```python
# tests/test_helpers/test_dto.py

from datetime import datetime
from helpers.DtO import parse_datetime, format_datetime, time_since

class TestDatetimeOperations:
    """Test datetime operation utilities."""
    
    def test_parse_datetime_default_format(self):
        """Test parsing datetime with default format."""
        result = parse_datetime("2024-01-15 14:30:00")
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 14
        assert result.minute == 30
    
    def test_format_datetime_custom_format(self):
        """Test formatting datetime with custom format."""
        dt = datetime(2024, 1, 15, 14, 30, 0)
        result = format_datetime(dt, "%Y/%m/%d")
        assert result == "2024/01/15"
    
    def test_time_since_calculates_delta(self):
        """Test time since calculation."""
        past = datetime(2024, 1, 1, 0, 0, 0)
        now = datetime(2024, 1, 2, 0, 0, 0)
        result = time_since(past, now)
        assert "1 day" in result
```

**Example: Testing File Operations**

```python
# tests/test_helpers/test_fado.py

import os
import tempfile
import pytest
from helpers.FaDO import create_directory, delete_directory

class TestFileOperations:
    """Test file and directory operations."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        # Cleanup after test
        if os.path.exists(temp_path):
            os.rmdir(temp_path)
    
    def test_create_directory_success(self, temp_dir):
        """Test successful directory creation."""
        test_path = os.path.join(temp_dir, "test_directory")
        create_directory(test_path)
        assert os.path.exists(test_path)
        assert os.path.isdir(test_path)
        # Cleanup
        os.rmdir(test_path)
    
    def test_create_directory_already_exists(self, temp_dir, capsys):
        """Test creating directory that already exists."""
        # Create directory first
        os.makedirs(os.path.join(temp_dir, "existing"))
        
        # Try to create again
        create_directory(os.path.join(temp_dir, "existing"))
        
        # Check that warning was printed
        captured = capsys.readouterr()
        assert "already exists" in captured.out
        
        # Cleanup
        os.rmdir(os.path.join(temp_dir, "existing"))
    
    def test_delete_directory_success(self, temp_dir):
        """Test successful directory deletion."""
        test_path = os.path.join(temp_dir, "to_delete")
        os.makedirs(test_path)
        
        delete_directory(test_path)
        assert not os.path.exists(test_path)
```

### Testing with Fixtures

Fixtures provide reusable test setup and teardown:

```python
# tests/conftest.py

import pytest
import tempfile
import os

@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return {
        'users': [
            {'id': 1, 'name': 'Alice'},
            {'id': 2, 'name': 'Bob'},
        ],
        'items': ['apple', 'banana', 'cherry']
    }

@pytest.fixture
def temp_directory():
    """Create and cleanup temporary directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    os.rmdir(temp_dir)

@pytest.fixture
def mock_config():
    """Provide mock configuration."""
    return {
        'api_key': 'test_key',
        'endpoint': 'https://api.test.com',
        'timeout': 30
    }
```

**Using fixtures in tests**:

```python
def test_with_sample_data(sample_data):
    """Test using sample data fixture."""
    assert len(sample_data['users']) == 2
    assert sample_data['users'][0]['name'] == 'Alice'

def test_with_temp_dir(temp_directory):
    """Test using temporary directory fixture."""
    test_file = os.path.join(temp_directory, 'test.txt')
    with open(test_file, 'w') as f:
        f.write('test content')
    
    assert os.path.exists(test_file)
```

### Testing Exceptions

```python
import pytest

def test_division_by_zero():
    """Test that division by zero raises exception."""
    with pytest.raises(ZeroDivisionError):
        result = 1 / 0

def test_invalid_input_raises_value_error():
    """Test that invalid input raises ValueError."""
    def process_positive(n):
        if n < 0:
            raise ValueError("Number must be positive")
        return n * 2
    
    with pytest.raises(ValueError, match="must be positive"):
        process_positive(-1)
```

### Parametrized Tests

Test multiple inputs efficiently:

```python
import pytest
from helpers.StrO import to_snake_case

@pytest.mark.parametrize("input_str,expected", [
    ("MyVariable", "my_variable"),
    ("myVariable", "my_variable"),
    ("my_variable", "my_variable"),
    ("MY_VARIABLE", "my_variable"),
    ("My Variable Name", "my_variable_name"),
])
def test_to_snake_case_variations(input_str, expected):
    """Test snake_case conversion with various inputs."""
    assert to_snake_case(input_str) == expected
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_helpers/test_stro.py

# Run specific test function
pytest tests/test_helpers/test_stro.py::test_to_snake_case_simple

# Run specific test class
pytest tests/test_helpers/test_stro.py::TestStringOperations

# Run tests matching pattern
pytest -k "snake_case"
```

### Verbose Output

```bash
# Show detailed output
pytest -v

# Show even more detail
pytest -vv

# Show print statements
pytest -s
```

### Test Discovery

```bash
# Discover and list tests without running
pytest --collect-only

# Show test execution order
pytest -v --collect-only
```

### Stopping on Failures

```bash
# Stop after first failure
pytest -x

# Stop after N failures
pytest --maxfail=3
```

## Test Coverage

### Measuring Coverage

```bash
# Run tests with coverage
pytest --cov=helpers --cov=Agents

# Generate HTML coverage report
pytest --cov=helpers --cov=Agents --cov-report=html

# View coverage report
open htmlcov/index.html  # On Mac
# or
xdg-open htmlcov/index.html  # On Linux
```

### Coverage Configuration

Create `.coveragerc`:

```ini
[run]
source = helpers,Agents
omit = 
    */tests/*
    */venv/*
    */__pycache__/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
```

### Coverage Goals

- **Helper modules**: Aim for 80%+ coverage
- **Critical paths**: Aim for 90%+ coverage
- **Agent logic**: Aim for 70%+ coverage

## Best Practices

### 1. Test One Thing at a Time

```python
# ✓ Good - focused test
def test_user_creation_sets_username():
    """Test that user creation sets the username."""
    user = User("alice")
    assert user.username == "alice"

# ✗ Avoid - testing too many things
def test_user_everything():
    """Test user creation and all methods."""
    user = User("alice")
    assert user.username == "alice"
    assert user.is_active()
    assert user.get_role() == "user"
    # ... many more assertions
```

### 2. Use Descriptive Test Names

```python
# ✓ Good - clear what's being tested
def test_empty_list_returns_zero_average():
    assert calculate_average([]) == 0

# ✗ Avoid - unclear purpose
def test_avg():
    assert calculate_average([]) == 0
```

### 3. Follow AAA Pattern

Arrange, Act, Assert:

```python
def test_user_login():
    # Arrange - setup test data
    user = User("alice", "password123")
    
    # Act - perform the action
    result = user.login("password123")
    
    # Assert - verify the outcome
    assert result is True
    assert user.is_authenticated
```

### 4. Keep Tests Independent

```python
# ✓ Good - tests are independent
class TestUserOperations:
    def test_create_user(self):
        user = User("alice")
        assert user.username == "alice"
    
    def test_delete_user(self):
        user = User("bob")
        user.delete()
        assert user.is_deleted

# ✗ Avoid - tests depend on each other
class TestUserOperations:
    def test_1_create_user(self):
        self.user = User("alice")
    
    def test_2_use_user(self):
        # Depends on test_1 running first
        assert self.user.username == "alice"
```

### 5. Use Fixtures for Common Setup

```python
# ✓ Good - reusable fixture
@pytest.fixture
def configured_app():
    app = App()
    app.configure({'debug': True})
    return app

def test_app_debug_enabled(configured_app):
    assert configured_app.debug is True

def test_app_can_process(configured_app):
    result = configured_app.process("data")
    assert result is not None
```

### 6. Test Edge Cases

```python
def test_calculate_average_edge_cases():
    """Test average calculation with edge cases."""
    # Empty list
    assert calculate_average([]) == 0
    
    # Single item
    assert calculate_average([5]) == 5
    
    # Negative numbers
    assert calculate_average([-1, -2, -3]) == -2
    
    # Mixed positive and negative
    assert calculate_average([-10, 10]) == 0
```

### 7. Mock External Dependencies

```python
from unittest.mock import Mock, patch

def test_api_call_success():
    """Test API call with mocked response."""
    with patch('requests.get') as mock_get:
        # Configure mock
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'data': 'test'}
        
        # Test function that uses requests.get
        result = fetch_data_from_api()
        
        # Verify
        assert result == {'data': 'test'}
        mock_get.assert_called_once()
```

## Examples

### Complete Test Suite Example

```python
# tests/test_helpers/test_data_processor.py

import pytest
from unittest.mock import Mock, patch
from helpers.data_processor import DataProcessor

class TestDataProcessor:
    """Test suite for DataProcessor."""
    
    @pytest.fixture
    def processor(self):
        """Create a DataProcessor instance."""
        return DataProcessor(config={'batch_size': 10})
    
    @pytest.fixture
    def sample_items(self):
        """Provide sample items for processing."""
        return [
            {'id': 1, 'value': 100},
            {'id': 2, 'value': 200},
            {'id': 3, 'value': 300},
        ]
    
    def test_initialization(self, processor):
        """Test processor initialization."""
        assert processor.config['batch_size'] == 10
        assert processor.processed_count == 0
    
    def test_process_single_item_success(self, processor):
        """Test processing single valid item."""
        item = {'id': 1, 'value': 100}
        result = processor.process_item(item)
        
        assert result['id'] == 1
        assert result['processed'] is True
    
    def test_process_batch_success(self, processor, sample_items):
        """Test batch processing of valid items."""
        results = processor.process_batch(sample_items)
        
        assert len(results) == 3
        assert all(r['processed'] for r in results)
        assert processor.processed_count == 3
    
    def test_process_invalid_item_raises_error(self, processor):
        """Test that invalid item raises ValueError."""
        invalid_item = {'id': 'invalid', 'value': 'not_a_number'}
        
        with pytest.raises(ValueError):
            processor.process_item(invalid_item)
    
    @pytest.mark.parametrize("value,expected", [
        (100, 110),  # 10% increase
        (200, 220),
        (0, 0),
    ])
    def test_calculate_markup(self, processor, value, expected):
        """Test markup calculation with various values."""
        result = processor.calculate_markup(value)
        assert result == expected
    
    def test_process_batch_with_errors(self, processor, capsys):
        """Test batch processing handles errors gracefully."""
        items = [
            {'id': 1, 'value': 100},
            {'id': 'invalid', 'value': 'bad'},  # Invalid
            {'id': 3, 'value': 300},
        ]
        
        results = processor.process_batch(items, skip_errors=True)
        
        # Should process valid items only
        assert len(results) == 2
        assert processor.error_count == 1
    
    @patch('helpers.data_processor.external_api')
    def test_fetch_external_data(self, mock_api, processor):
        """Test fetching data from external API."""
        # Configure mock
        mock_api.get_data.return_value = {'status': 'success', 'data': [1, 2, 3]}
        
        # Test
        result = processor.fetch_external_data('endpoint')
        
        # Verify
        assert result['status'] == 'success'
        assert len(result['data']) == 3
        mock_api.get_data.assert_called_once_with('endpoint')
```

### Testing Async Code

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_operation():
    """Test asynchronous operation."""
    result = await async_fetch_data()
    assert result is not None

@pytest.mark.asyncio
async def test_async_with_timeout():
    """Test async operation with timeout."""
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(slow_async_operation(), timeout=1.0)
```

## Continuous Integration

### GitHub Actions Example

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install pytest pytest-cov
        # Install other dependencies
    
    - name: Run tests
      run: |
        pytest --cov=helpers --cov=Agents --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## Summary

- Use pytest as the testing framework
- Organize tests in a `tests/` directory
- Write focused, independent tests
- Use fixtures for common setup
- Test edge cases and error conditions
- Measure and improve test coverage
- Run tests frequently during development
- Integrate tests into CI/CD pipeline

For more information:
- [Pytest Documentation](https://docs.pytest.org/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)
- [TUTORIALS.md](TUTORIALS.md) - Testing tutorial
