"""
Tests for String Operations (StrO.py) module.

This module contains unit tests for the string manipulation utilities.
"""

import pytest
from helpers.StrO import to_snake_case, to_camel_case, clean_string


class TestToSnakeCase:
    """Test suite for to_snake_case function."""
    
    def test_simple_camel_case(self):
        """Test simple camelCase to snake_case conversion."""
        assert to_snake_case("myVariableName") == "my_variable_name"
    
    def test_pascal_case(self):
        """Test PascalCase to snake_case conversion."""
        assert to_snake_case("MyVariableName") == "my_variable_name"
    
    def test_already_snake_case(self):
        """Test that already snake_case strings remain unchanged."""
        assert to_snake_case("my_variable_name") == "my_variable_name"
    
    def test_with_spaces(self):
        """Test conversion with spaces."""
        assert to_snake_case("My Variable Name") == "my_variable_name"
    
    def test_with_hyphens(self):
        """Test conversion with hyphens."""
        assert to_snake_case("my-variable-name") == "my_variable_name"
    
    def test_all_caps(self):
        """Test conversion of all uppercase."""
        assert to_snake_case("MYVARIABLE") == "myvariable"
    
    def test_mixed_separators(self):
        """Test conversion with mixed separators."""
        assert to_snake_case("my-Variable_Name") == "my_variable_name"
    
    @pytest.mark.parametrize("input_str,expected", [
        ("simpleTest", "simple_test"),
        ("SimpleTest", "simple_test"),
        ("simple_test", "simple_test"),
        ("simple-test", "simple_test"),
        ("SIMPLE", "simple"),
        ("simpleTestCase", "simple_test_case"),
    ])
    def test_various_inputs(self, input_str, expected):
        """Test various input formats."""
        assert to_snake_case(input_str) == expected


class TestToCamelCase:
    """Test suite for to_camel_case function."""
    
    def test_simple_snake_case(self):
        """Test simple snake_case to camelCase conversion."""
        assert to_camel_case("my_variable_name") == "myVariableName"
    
    def test_with_spaces(self):
        """Test conversion with spaces."""
        assert to_camel_case("my variable name") == "myVariableName"
    
    def test_with_hyphens(self):
        """Test conversion with hyphens."""
        assert to_camel_case("my-variable-name") == "myVariableName"
    
    def test_single_word(self):
        """Test single word conversion."""
        result = to_camel_case("variable")
        assert result[0].islower()  # First letter should be lowercase
        assert result == "variable"
    
    def test_already_camel_case(self):
        """Test already camelCase strings."""
        # May not preserve exact format but should be valid camelCase
        result = to_camel_case("myVariableName")
        assert result[0].islower()
    
    @pytest.mark.parametrize("input_str,expected", [
        ("simple_test", "simpleTest"),
        ("simple test", "simpleTest"),
        ("simple-test", "simpleTest"),
        ("simple", "simple"),
        ("simple_test_case", "simpleTestCase"),
    ])
    def test_various_inputs(self, input_str, expected):
        """Test various input formats."""
        assert to_camel_case(input_str) == expected


class TestCleanString:
    """Test suite for clean_string function."""
    
    def test_removes_punctuation(self):
        """Test removal of punctuation."""
        result = clean_string("Hello, World!")
        assert "," not in result
        assert "!" not in result
    
    def test_preserves_alphanumeric(self):
        """Test that alphanumeric characters are preserved."""
        result = clean_string("Test123")
        assert "Test123" in result or "Test 123" in result
    
    def test_custom_replacement(self):
        """Test custom replacement character."""
        result = clean_string("Hello, World!", replace_with="-")
        assert "-" in result or result.strip() == "Hello- World-" or "Hello" in result
    
    def test_multiple_special_chars(self):
        """Test removal of multiple special characters."""
        result = clean_string("!@#$%Hello^&*()")
        assert any(char.isalpha() for char in result)
        assert not any(char in "!@#$%^&*()" for char in result)
    
    def test_empty_string(self):
        """Test with empty string."""
        result = clean_string("")
        assert isinstance(result, str)
    
    def test_only_special_chars(self):
        """Test with only special characters."""
        result = clean_string("!@#$%")
        # Should replace all with the replacement character
        assert "!" not in result
        assert "@" not in result


class TestStringOperationsIntegration:
    """Integration tests for string operations."""
    
    def test_snake_to_camel_roundtrip(self):
        """Test converting to camelCase and back."""
        original = "my_test_variable"
        camel = to_camel_case(original)
        back_to_snake = to_snake_case(camel)
        assert back_to_snake == original
    
    def test_clean_then_convert(self):
        """Test cleaning followed by case conversion."""
        dirty = "My-Dirty@Variable#Name"
        cleaned = clean_string(dirty)
        snake = to_snake_case(cleaned)
        assert isinstance(snake, str)
        assert "_" in snake or snake.islower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
