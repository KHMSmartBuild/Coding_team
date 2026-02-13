"""
Tests for the Tools module.

This module contains unit tests for the Tool classes,
ToolRegistry, and related functionality.
"""

import pytest
from core.tools import (
    Tool,
    ToolParameter,
    ToolResult,
    ToolRegistry,
    FunctionTool,
    CodeAnalysisTool,
    FileOperationTool,
    ParameterType,
    tool,
    ReadFileTool,
    WriteFileTool,
    SearchCodeTool,
    ExecuteCodeTool,
    get_default_tools,
)


class TestToolParameter:
    """Test suite for ToolParameter dataclass."""

    def test_parameter_creation(self):
        """Test basic parameter creation."""
        param = ToolParameter(
            name="query",
            type="string",
            description="Search query",
            required=True
        )
        assert param.name == "query"
        assert param.type == "string"
        assert param.required is True

    def test_optional_parameter(self):
        """Test optional parameter with default."""
        param = ToolParameter(
            name="limit",
            type="integer",
            required=False,
            default=10
        )
        assert param.required is False
        assert param.default == 10

    def test_parameter_with_enum(self):
        """Test parameter with enum values."""
        param = ToolParameter(
            name="format",
            type="string",
            enum=["json", "xml", "csv"]
        )
        assert param.enum == ["json", "xml", "csv"]

    def test_to_json_schema(self):
        """Test conversion to JSON Schema."""
        param = ToolParameter(
            name="query",
            type="string",
            description="Search query"
        )
        schema = param.to_json_schema()
        assert schema["type"] == "string"
        assert schema["description"] == "Search query"

    def test_to_json_schema_with_enum(self):
        """Test JSON Schema includes enum."""
        param = ToolParameter(
            name="format",
            type="string",
            enum=["a", "b"]
        )
        schema = param.to_json_schema()
        assert schema["enum"] == ["a", "b"]


class TestToolResult:
    """Test suite for ToolResult dataclass."""

    def test_success_result(self):
        """Test successful result creation."""
        result = ToolResult(success=True, output="Done")
        assert result.success is True
        assert result.output == "Done"
        assert result.error is None

    def test_error_result(self):
        """Test error result creation."""
        result = ToolResult(success=False, error="Something failed")
        assert result.success is False
        assert result.error == "Something failed"

    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = ToolResult(
            success=True,
            output="data",
            tool_name="test_tool"
        )
        d = result.to_dict()
        assert d["success"] is True
        assert d["output"] == "data"
        assert d["tool_name"] == "test_tool"

    def test_str_success(self):
        """Test string representation for success."""
        result = ToolResult(success=True, output="OK", tool_name="test")
        s = str(result)
        assert "[test]" in s
        assert "Success" in s

    def test_str_error(self):
        """Test string representation for error."""
        result = ToolResult(success=False, error="Failed", tool_name="test")
        s = str(result)
        assert "[test]" in s
        assert "Error" in s


class TestFunctionTool:
    """Test suite for FunctionTool class."""

    def test_wrap_function(self):
        """Test wrapping a simple function."""
        def add(a: int, b: int) -> int:
            return a + b

        tool = FunctionTool(add, name="add", description="Add numbers")
        assert tool.name == "add"
        assert tool.description == "Add numbers"

    def test_auto_name_from_function(self):
        """Test automatic name extraction from function."""
        def my_function():
            pass

        tool = FunctionTool(my_function)
        assert tool.name == "my_function"

    def test_execute_function(self):
        """Test executing wrapped function."""
        def multiply(x: int, y: int) -> int:
            return x * y

        tool = FunctionTool(multiply)
        result = tool.execute(x=3, y=4)
        assert result.success is True
        assert result.output == 12

    def test_execute_with_error(self):
        """Test execution error handling."""
        def failing_func():
            raise ValueError("Test error")

        tool = FunctionTool(failing_func)
        result = tool.execute()
        assert result.success is False
        assert "Test error" in result.error

    def test_call_method(self):
        """Test calling tool directly."""
        def greet(name: str) -> str:
            return f"Hello, {name}"

        tool = FunctionTool(greet)
        result = tool(name="World")
        assert result.success is True
        assert result.output == "Hello, World"

    def test_parameter_extraction(self):
        """Test automatic parameter extraction."""
        def func(required_param: str, optional_param: int = 10):
            pass

        tool = FunctionTool(func)
        params = {p.name: p for p in tool.parameters}

        assert "required_param" in params
        assert params["required_param"].required is True
        assert "optional_param" in params
        assert params["optional_param"].required is False

    def test_get_schema(self):
        """Test getting tool schema."""
        def search(query: str) -> str:
            return query

        tool = FunctionTool(search, name="search", description="Search")
        schema = tool.get_schema()

        assert schema["type"] == "function"
        assert schema["function"]["name"] == "search"
        assert "parameters" in schema["function"]


class TestToolDecorator:
    """Test suite for Tool.define decorator."""

    def test_define_decorator(self):
        """Test using @Tool.define decorator."""
        @Tool.define(name="greet", description="Say hello")
        def greet_user(name: str) -> str:
            return f"Hello, {name}"

        assert isinstance(greet_user, FunctionTool)
        assert greet_user.name == "greet"
        result = greet_user(name="Test")
        assert result.output == "Hello, Test"


class TestToolRegistry:
    """Test suite for ToolRegistry class."""

    def test_registry_initialization(self):
        """Test registry initializes empty."""
        registry = ToolRegistry()
        assert len(registry) == 0

    def test_register_tool(self):
        """Test registering a tool."""
        registry = ToolRegistry()

        def my_tool():
            return "result"

        registry.register(my_tool)
        assert "my_tool" in registry
        assert len(registry) == 1

    def test_register_with_category(self):
        """Test registering tool with category."""
        registry = ToolRegistry()

        def my_tool():
            pass

        registry.register(my_tool, category="utils")
        assert "utils" in registry.list_categories()
        assert "my_tool" in registry.list_tools(category="utils")

    def test_unregister_tool(self):
        """Test unregistering a tool."""
        registry = ToolRegistry()

        def my_tool():
            pass

        registry.register(my_tool)
        assert "my_tool" in registry

        result = registry.unregister("my_tool")
        assert result is True
        assert "my_tool" not in registry

    def test_unregister_nonexistent(self):
        """Test unregistering nonexistent tool returns False."""
        registry = ToolRegistry()
        result = registry.unregister("nonexistent")
        assert result is False

    def test_get_tool(self):
        """Test getting a tool by name."""
        registry = ToolRegistry()

        def my_tool():
            return "result"

        registry.register(my_tool)
        tool = registry.get("my_tool")
        assert tool is not None
        assert tool.name == "my_tool"

    def test_get_nonexistent_returns_none(self):
        """Test getting nonexistent tool returns None."""
        registry = ToolRegistry()
        tool = registry.get("nonexistent")
        assert tool is None

    def test_execute_tool(self):
        """Test executing a tool through registry."""
        registry = ToolRegistry()

        def add(x: int, y: int) -> int:
            return x + y

        registry.register(add)
        result = registry.execute("add", x=2, y=3)
        assert result.success is True
        assert result.output == 5

    def test_execute_nonexistent_raises_error(self):
        """Test executing nonexistent tool raises KeyError."""
        registry = ToolRegistry()
        with pytest.raises(KeyError):
            registry.execute("nonexistent")

    def test_list_tools(self):
        """Test listing all tools."""
        registry = ToolRegistry()

        def tool_a():
            pass

        def tool_b():
            pass

        registry.register(tool_a)
        registry.register(tool_b)

        tools = registry.list_tools()
        assert "tool_a" in tools
        assert "tool_b" in tools

    def test_get_all_schemas(self):
        """Test getting all tool schemas."""
        registry = ToolRegistry()

        def my_tool(x: str) -> str:
            return x

        registry.register(my_tool)
        schemas = registry.get_all_schemas()

        assert len(schemas) == 1
        assert schemas[0]["function"]["name"] == "my_tool"

    def test_to_openai_format(self):
        """Test OpenAI format conversion."""
        registry = ToolRegistry()

        def test_func():
            pass

        registry.register(test_func)
        openai_tools = registry.to_openai_format()

        assert len(openai_tools) == 1
        assert openai_tools[0]["type"] == "function"

    def test_method_chaining(self):
        """Test method chaining for registration."""
        registry = ToolRegistry()

        def a():
            pass

        def b():
            pass

        registry.register(a).register(b)
        assert len(registry) == 2


class TestBuiltInTools:
    """Test suite for built-in tools."""

    def test_code_analysis_tool(self):
        """Test CodeAnalysisTool."""
        tool = CodeAnalysisTool()
        assert tool.name == "code_analysis"

        result = tool(code="def foo():\n    pass", language="python")
        assert result.success is True
        assert "lines" in result.output
        assert result.output["lines"] == 2

    def test_code_analysis_style_check(self):
        """Test code analysis style checking."""
        tool = CodeAnalysisTool()
        # Line longer than 79 chars (PEP8 max line length)
        max_line_length = 79
        long_line = "x = " + "a" * (max_line_length + 21)
        result = tool(code=long_line, checks=["style"])

        assert result.success is True
        issues = result.output.get("issues", [])
        assert len(issues) > 0

    def test_file_operation_exists(self):
        """Test file operation exists check."""
        tool = FileOperationTool()
        result = tool(operation="exists", path="/tmp")

        assert result.success is True
        assert result.output is True

    def test_file_operation_rejects_null_bytes(self):
        """Test that file operation rejects paths with null bytes."""
        tool = FileOperationTool()
        result = tool(operation="exists", path="/tmp/test\x00file.txt")

        assert result.success is False
        assert "null bytes" in result.error.lower()

    def test_file_operation_requires_path(self):
        """Test that file operation requires a path."""
        tool = FileOperationTool()
        result = tool(operation="exists", path="")

        assert result.success is False
        assert "required" in result.error.lower()

    def test_file_operation_list(self):
        """Test file operation list."""
        tool = FileOperationTool()
        result = tool(operation="list", path="/tmp")

        assert result.success is True
        assert isinstance(result.output, list)


class TestGetDefaultTools:
    """Test suite for get_default_tools function."""

    def test_get_default_tools(self):
        """Test getting default tool registry."""
        registry = get_default_tools()
        assert isinstance(registry, ToolRegistry)
        assert len(registry) > 0

    def test_default_tools_include_code_analysis(self):
        """Test default tools include code analysis."""
        registry = get_default_tools()
        assert "code_analysis" in registry

    def test_default_tools_include_file_operation(self):
        """Test default tools include file operation."""
        registry = get_default_tools()
        assert "file_operation" in registry

    def test_default_tools_include_test_runner(self):
        """Test default tools include test runner."""
        registry = get_default_tools()
        assert "test_runner" in registry

    def test_default_tools_include_new_tools(self):
        """Test default tools include newly added tools."""
        registry = get_default_tools()
        assert "read_file" in registry
        assert "write_file" in registry
        assert "search_code" in registry
        assert "execute_code" in registry


class TestParameterType:
    """Test suite for ParameterType enum."""

    def test_parameter_type_values(self):
        """Test ParameterType enum has correct values."""
        assert ParameterType.STRING.value == "string"
        assert ParameterType.INTEGER.value == "integer"
        assert ParameterType.NUMBER.value == "number"
        assert ParameterType.BOOLEAN.value == "boolean"
        assert ParameterType.ARRAY.value == "array"
        assert ParameterType.OBJECT.value == "object"

    def test_parameter_with_enum_type(self):
        """Test ToolParameter with ParameterType enum."""
        param = ToolParameter(
            name="count",
            type=ParameterType.INTEGER,
            description="Number of items"
        )
        assert param.type == ParameterType.INTEGER
        schema = param.to_json_schema()
        assert schema["type"] == "integer"

    def test_parameter_backward_compatibility(self):
        """Test ToolParameter still accepts string types."""
        param = ToolParameter(
            name="query",
            type="string",
            description="Search query"
        )
        schema = param.to_json_schema()
        assert schema["type"] == "string"


class TestToolDecorator:
    """Test suite for @tool decorator."""

    def test_tool_decorator_with_name(self):
        """Test @tool decorator with custom name."""
        @tool(name="custom_name", description="Custom description")
        def my_function(x: int) -> int:
            return x * 2

        assert isinstance(my_function, FunctionTool)
        assert my_function.name == "custom_name"
        assert my_function.description == "Custom description"

    def test_tool_decorator_defaults(self):
        """Test @tool decorator with default values."""
        @tool()
        def calculate(a: int, b: int) -> int:
            """Calculate sum of two numbers."""
            return a + b

        assert calculate.name == "calculate"
        assert "Calculate sum" in calculate.description

    def test_tool_decorator_execution(self):
        """Test executing tool created with @tool decorator."""
        @tool(name="multiply")
        def multiply(x: int, y: int) -> int:
            return x * y

        result = multiply(x=3, y=4)
        assert result.success is True
        assert result.output == 12


class TestExecuteCodeTool:
    """Test suite for ExecuteCodeTool with comprehensive security tests."""

    def test_execute_code_tool_initialization(self):
        """Test ExecuteCodeTool initializes correctly."""
        tool = ExecuteCodeTool()
        assert tool.name == "execute_code"
        assert len(tool.DANGEROUS_PATTERNS) == 16

    def test_execute_safe_code(self):
        """Test executing safe Python code."""
        tool = ExecuteCodeTool()
        result = tool(code="x = 1 + 1")
        assert result.success is True

    def test_execute_code_with_print(self):
        """Test executing code with print statement."""
        tool = ExecuteCodeTool()
        result = tool(code="print('Hello, World!')")
        assert result.success is True
        assert "Hello, World!" in result.output["stdout"]

    # Parameterized tests for all 16 dangerous patterns
    @pytest.mark.parametrize("code,expected_error", [
        # 1. os module from import (checked first)
        ("from os import path", "Importing from 'os' module is not allowed"),
        # 2. os module import
        ("import os", "Importing 'os' module is not allowed"),
        # 3. sys module from import (checked first)
        ("from sys import argv", "Importing from 'sys' module is not allowed"),
        # 4. sys module import
        ("import sys", "Importing 'sys' module is not allowed"),
        # 5. subprocess module from import (checked first)
        ("from subprocess import run", "Importing from 'subprocess' module is not allowed"),
        # 6. subprocess module import
        ("import subprocess", "Importing 'subprocess' module is not allowed"),
        # 7. socket module from import (checked first)
        ("from socket import socket", "Importing from 'socket' module is not allowed"),
        # 8. socket module import
        ("import socket", "Importing 'socket' module is not allowed"),
        # 9. exec() function
        ("exec('print(1)')", "Using 'exec()' is not allowed"),
        # 10. eval() function
        ("eval('1 + 1')", "Using 'eval()' is not allowed"),
        # 11. compile() function
        ("compile('x=1', '<string>', 'exec')", "Using 'compile()' is not allowed"),
        # 12. __import__() function
        ("__import__('os')", "Using '__import__()' is not allowed"),
        # 13. open() function
        ("open('file.txt', 'r')", "Using 'open()' is not allowed"),
        # 14. globals() function
        ("globals()", "Using 'globals()' is not allowed"),
        # 15. locals() function
        ("locals()", "Using 'locals()' is not allowed"),
        # 16. vars() function
        ("vars()", "Using 'vars()' is not allowed"),
        # Additional test cases with variations
        ("import os.path", "Importing 'os' module is not allowed"),
        ("IMPORT OS", "Importing 'os' module is not allowed"),  # Case insensitive
        ("x = eval('1+1')", "Using 'eval()' is not allowed"),
    ])
    def test_dangerous_patterns_blocked(self, code, expected_error):
        """Test that all dangerous patterns are properly blocked."""
        tool = ExecuteCodeTool()
        result = tool(code=code)
        assert result.success is False
        assert expected_error in result.error

    def test_execute_code_requires_code_parameter(self):
        """Test that code parameter is required."""
        tool = ExecuteCodeTool()
        result = tool(code="")
        assert result.success is False
        assert "required" in result.error.lower()

    def test_execute_code_with_error(self):
        """Test executing code that raises an exception."""
        tool = ExecuteCodeTool()
        result = tool(code="x = 1 / 0")
        assert result.success is False
        assert "error" in result.error.lower()

    def test_execute_code_restricted_builtins(self):
        """Test that only safe builtins are available."""
        tool = ExecuteCodeTool()
        # Test that basic builtins work
        result = tool(code="x = len([1, 2, 3])")
        assert result.success is True


class TestReadFileTool:
    """Test suite for ReadFileTool."""

    def test_read_file_tool_initialization(self):
        """Test ReadFileTool initializes correctly."""
        tool = ReadFileTool()
        assert tool.name == "read_file"
        assert len(tool.parameters) == 1

    def test_read_file_requires_path(self):
        """Test that path parameter is required."""
        tool = ReadFileTool()
        result = tool(path="")
        assert result.success is False
        assert "required" in result.error.lower()

    def test_read_file_rejects_null_bytes(self):
        """Test that null bytes in path are rejected."""
        tool = ReadFileTool()
        result = tool(path="/tmp/test\x00file.txt")
        assert result.success is False
        assert "null bytes" in result.error.lower()


class TestWriteFileTool:
    """Test suite for WriteFileTool."""

    def test_write_file_tool_initialization(self):
        """Test WriteFileTool initializes correctly."""
        tool = WriteFileTool()
        assert tool.name == "write_file"
        assert len(tool.parameters) == 2

    def test_write_file_requires_path(self):
        """Test that path parameter is required."""
        tool = WriteFileTool()
        result = tool(path="", content="test")
        assert result.success is False
        assert "required" in result.error.lower()

    def test_write_file_rejects_null_bytes(self):
        """Test that null bytes in path are rejected."""
        tool = WriteFileTool()
        result = tool(path="/tmp/test\x00file.txt", content="test")
        assert result.success is False
        assert "null bytes" in result.error.lower()


class TestSearchCodeTool:
    """Test suite for SearchCodeTool."""

    def test_search_code_tool_initialization(self):
        """Test SearchCodeTool initializes correctly."""
        tool = SearchCodeTool()
        assert tool.name == "search_code"
        assert len(tool.parameters) == 3

    def test_search_code_requires_parameters(self):
        """Test that pattern and path are required."""
        tool = SearchCodeTool()
        result = tool(pattern="", path="")
        assert result.success is False
        assert "required" in result.error.lower()

    def test_search_code_invalid_regex(self):
        """Test handling of invalid regex patterns."""
        tool = SearchCodeTool()
        result = tool(pattern="[invalid(", path="/tmp")
        assert result.success is False
        assert "regex" in result.error.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
