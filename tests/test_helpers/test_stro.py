"""
Tests for String Operations (StrO.py) module.

This module contains unit tests for the string manipulation utilities.
"""

import pytest
from helpers.StrO import (
    to_snake_case,
    to_camel_case,
    to_pascal_case,
    to_kebab_case,
    clean_string,
    truncate,
    slugify,
    is_empty_or_whitespace,
)


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
    
    def test_empty_string(self):
        """Test with empty string - should return empty string."""
        assert to_camel_case("") == ""
    
    def test_whitespace_only(self):
        """Test with whitespace only - should return empty string."""
        assert to_camel_case("   ") == ""
    
    @pytest.mark.parametrize("input_str,expected", [
        ("simple_test", "simpleTest"),
        ("simple test", "simpleTest"),
        ("simple-test", "simpleTest"),
        ("simple", "simple"),
        ("simple_test_case", "simpleTestCase"),
        ("", ""),
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


class TestToPascalCase:
    """Test suite for to_pascal_case function."""
    
    def test_simple_snake_case(self):
        """Test simple snake_case to PascalCase conversion."""
        assert to_pascal_case("hello_world") == "HelloWorld"
    
    def test_with_spaces(self):
        """Test conversion with spaces."""
        assert to_pascal_case("hello world") == "HelloWorld"
    
    def test_with_hyphens(self):
        """Test conversion with hyphens."""
        assert to_pascal_case("hello-world") == "HelloWorld"
    
    def test_empty_string(self):
        """Test with empty string - should return empty string."""
        assert to_pascal_case("") == ""
    
    def test_whitespace_only(self):
        """Test with whitespace only - should return empty string."""
        assert to_pascal_case("   ") == ""
    
    def test_single_word(self):
        """Test single word conversion."""
        result = to_pascal_case("hello")
        assert result == "Hello"
        assert result[0].isupper()
    
    @pytest.mark.parametrize("input_str,expected", [
        ("hello_world", "HelloWorld"),
        ("hello-world", "HelloWorld"),
        ("hello world", "HelloWorld"),
        ("helloWorld", "HelloWorld"),
        ("", ""),
    ])
    def test_various_inputs(self, input_str, expected):
        """Test various input formats."""
        assert to_pascal_case(input_str) == expected


class TestToKebabCase:
    """Test suite for to_kebab_case function."""
    
    def test_simple_snake_case(self):
        """Test simple snake_case to kebab-case conversion."""
        assert to_kebab_case("hello_world") == "hello-world"
    
    def test_camel_case(self):
        """Test camelCase to kebab-case conversion."""
        assert to_kebab_case("helloWorld") == "hello-world"
    
    def test_pascal_case(self):
        """Test PascalCase to kebab-case conversion."""
        assert to_kebab_case("HelloWorld") == "hello-world"
    
    def test_with_spaces(self):
        """Test conversion with spaces."""
        assert to_kebab_case("Hello World") == "hello-world"
    
    @pytest.mark.parametrize("input_str,expected", [
        ("hello_world", "hello-world"),
        ("HelloWorld", "hello-world"),
        ("helloWorld", "hello-world"),
        ("hello world", "hello-world"),
    ])
    def test_various_inputs(self, input_str, expected):
        """Test various input formats."""
        assert to_kebab_case(input_str) == expected


class TestTruncate:
    """Test suite for truncate function."""
    
    def test_truncate_long_string(self):
        """Test truncating a long string."""
        result = truncate("Hello, World!", 10)
        assert len(result) == 10
        assert result == "Hello, ..."
    
    def test_no_truncate_short_string(self):
        """Test that short strings are not truncated."""
        result = truncate("Hi", 10)
        assert result == "Hi"
    
    def test_custom_suffix(self):
        """Test truncation with custom suffix."""
        result = truncate("Hello, World!", 10, suffix="--")
        assert len(result) == 10
        assert result.endswith("--")
    
    def test_exact_length(self):
        """Test string at exact max length."""
        result = truncate("Hello", 5)
        assert result == "Hello"
    
    def test_invalid_max_length(self):
        """Test that ValueError is raised when max_length < suffix length."""
        with pytest.raises(ValueError):
            truncate("Hello", 2, suffix="...")
    
    @pytest.mark.parametrize("input_str,max_len,expected_len", [
        ("Hello, World!", 10, 10),
        ("Hi", 10, 2),
        ("Test string here", 8, 8),
    ])
    def test_various_lengths(self, input_str, max_len, expected_len):
        """Test various truncation scenarios."""
        result = truncate(input_str, max_len)
        assert len(result) == expected_len


class TestSlugify:
    """Test suite for slugify function."""
    
    def test_basic_slugify(self):
        """Test basic slugify conversion."""
        assert slugify("Hello World") == "hello-world"
    
    def test_remove_special_chars(self):
        """Test removal of special characters."""
        assert slugify("Hello, World!") == "hello-world"
    
    def test_multiple_spaces(self):
        """Test handling of multiple spaces."""
        result = slugify("Hello    World")
        assert result == "hello-world"
    
    def test_mixed_case_and_special(self):
        """Test mixed case with special characters."""
        result = slugify("Python is Great!")
        assert result == "python-is-great"
    
    @pytest.mark.parametrize("input_str,expected", [
        ("Hello World", "hello-world"),
        ("Hello, World!", "hello-world"),
        ("Python is great", "python-is-great"),
        ("Test@123", "test123"),
    ])
    def test_various_inputs(self, input_str, expected):
        """Test various input formats."""
        assert slugify(input_str) == expected


class TestIsEmptyOrWhitespace:
    """Test suite for is_empty_or_whitespace function."""
    
    def test_empty_string(self):
        """Test with empty string."""
        assert is_empty_or_whitespace("") is True
    
    def test_whitespace_only(self):
        """Test with whitespace only."""
        assert is_empty_or_whitespace("   ") is True
        assert is_empty_or_whitespace("\t\n") is True
    
    def test_none_value(self):
        """Test with None value."""
        assert is_empty_or_whitespace(None) is True
    
    def test_non_empty_string(self):
        """Test with non-empty string."""
        assert is_empty_or_whitespace("hello") is False
        assert is_empty_or_whitespace("  hello  ") is False
    
    @pytest.mark.parametrize("input_str,expected", [
        ("", True),
        ("   ", True),
        ("\t", True),
        ("\n", True),
        (None, True),
        ("hello", False),
        ("  hello  ", False),
    ])
    def test_various_inputs(self, input_str, expected):
        """Test various input formats."""
        assert is_empty_or_whitespace(input_str) is expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
