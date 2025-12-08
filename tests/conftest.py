"""
Shared pytest fixtures for the Coding_team test suite.

This module provides reusable fixtures that can be used across all test modules.
"""

import pytest
import tempfile
import os
import shutil
from pathlib import Path
from datetime import datetime


@pytest.fixture
def temp_dir():
    """
    Create a temporary directory for testing.
    
    Yields the path to the temporary directory and cleans up after the test.
    
    Example:
        def test_file_operations(temp_dir):
            test_file = temp_dir / "test.txt"
            test_file.write_text("test content")
            assert test_file.exists()
    """
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    # Cleanup
    if temp_path.exists():
        shutil.rmtree(temp_path)


@pytest.fixture
def sample_log_file(temp_dir):
    """
    Create a sample log file for testing log analysis.
    
    Returns path to a temporary log file with sample entries.
    
    Example:
        def test_log_parsing(sample_log_file):
            # Log file is ready to use
            assert sample_log_file.exists()
    """
    log_content = """2024-01-15 10:00:00 - INFO - Application started
2024-01-15 10:01:00 - DEBUG - Processing user request
2024-01-15 10:02:00 - WARNING - Slow database query detected
2024-01-15 10:03:00 - ERROR - Connection timeout
2024-01-15 10:04:00 - INFO - Request completed
2024-01-15 10:05:00 - CRITICAL - System failure detected
"""
    
    log_file = temp_dir / "test.log"
    log_file.write_text(log_content)
    return log_file


@pytest.fixture
def sample_data():
    """
    Provide sample data for testing.
    
    Returns a dictionary with various sample data structures.
    
    Example:
        def test_data_processing(sample_data):
            users = sample_data['users']
            assert len(users) == 3
    """
    return {
        'users': [
            {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'},
            {'id': 2, 'name': 'Bob', 'email': 'bob@example.com'},
            {'id': 3, 'name': 'Charlie', 'email': 'charlie@example.com'},
        ],
        'items': ['apple', 'banana', 'cherry', 'date', 'elderberry'],
        'numbers': [1, 2, 3, 4, 5, 10, 20, 30],
        'config': {
            'debug': True,
            'timeout': 30,
            'max_retries': 3,
        }
    }


@pytest.fixture
def sample_datetime():
    """
    Provide a consistent datetime for testing.
    
    Returns a fixed datetime object.
    
    Example:
        def test_datetime_formatting(sample_datetime):
            formatted = format_datetime(sample_datetime)
            assert "2024-01-15" in formatted
    """
    return datetime(2024, 1, 15, 14, 30, 0)


@pytest.fixture
def mock_config():
    """
    Provide mock configuration for testing.
    
    Returns a configuration dictionary suitable for testing.
    
    Example:
        def test_app_initialization(mock_config):
            app = App(mock_config)
            assert app.debug is True
    """
    return {
        'api_key': 'test_api_key_12345',
        'endpoint': 'https://api.test.example.com',
        'timeout': 30,
        'max_retries': 3,
        'debug': True,
        'log_level': 'DEBUG',
    }


@pytest.fixture(scope='session')
def project_root():
    """
    Get the project root directory.
    
    Returns the Path to the project root.
    Scope is 'session' so it's only calculated once.
    
    Example:
        def test_file_exists(project_root):
            readme = project_root / "README.md"
            assert readme.exists()
    """
    # Go up from tests directory to project root
    return Path(__file__).parent.parent


@pytest.fixture
def clean_environment(monkeypatch):
    """
    Provide a clean environment with no sensitive variables.
    
    Removes common sensitive environment variables for testing.
    
    Example:
        def test_without_api_key(clean_environment):
            # API key is not in environment
            assert 'API_KEY' not in os.environ
    """
    sensitive_vars = ['API_KEY', 'SECRET_KEY', 'PASSWORD', 'TOKEN']
    for var in sensitive_vars:
        monkeypatch.delenv(var, raising=False)


# Pytest configuration hooks

def pytest_configure(config):
    """
    Configure pytest with custom markers.
    
    This allows using custom markers like @pytest.mark.slow
    """
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )


def pytest_collection_modifyitems(config, items):
    """
    Modify test collection to add markers automatically.
    
    Adds the 'unit' marker to all tests by default unless they have
    the 'integration' or 'slow' markers.
    """
    for item in items:
        if "integration" not in item.keywords and "slow" not in item.keywords:
            item.add_marker(pytest.mark.unit)
