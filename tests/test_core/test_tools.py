"""Tests for the Tools Framework.

This module contains comprehensive tests for the tools framework including
tool creation, registry, and OpenAI function schema generation.
"""

import os
import pytest
import tempfile
from core.tools import (
    ExecuteCodeTool,
    FunctionTool,
    ParameterType,
    ReadFileTool,
    SearchCodeTool,
    Tool,
    ToolParameter,
    ToolRegistry,
    ToolSchema,
    WriteFileTool,
    create_default_registry,
    tool,
)


class TestParameterType:
    """Tests for ParameterType enum."""

    def test_string_value(self):
        """Test string parameter type."""
        assert ParameterType.STRING.value == "string"

    def test_integer_value(self):
        """Test integer parameter type."""
        assert ParameterType.INTEGER.value == "integer"

    def test_number_value(self):
        """Test number parameter type."""
        assert ParameterType.NUMBER.value == "number"

    def test_boolean_value(self):
        """Test boolean parameter type."""
        assert ParameterType.BOOLEAN.value == "boolean"

    def test_array_value(self):
        """Test array parameter type."""
        assert ParameterType.ARRAY.value == "array"

    def test_object_value(self):
        """Test object parameter type."""
        assert ParameterType.OBJECT.value == "object"


class TestToolParameter:
    """Tests for ToolParameter dataclass."""

    def test_create_required_parameter(self):
        """Test creating a required parameter."""
        param = ToolParameter(
            name="query",
            param_type=ParameterType.STRING,
            description="The search query",
            required=True,
        )
        assert param.name == "query"
        assert param.param_type == ParameterType.STRING
        assert param.description == "The search query"
        assert param.required is True

    def test_create_optional_parameter(self):
        """Test creating an optional parameter."""
        param = ToolParameter(
            name="limit",
            param_type=ParameterType.INTEGER,
            description="Maximum results",
            required=False,
            default=10,
        )
        assert param.required is False
        assert param.default == 10

    def test_parameter_with_enum(self):
        """Test parameter with enum values."""
        param = ToolParameter(
            name="operation",
            param_type=ParameterType.STRING,
            description="Operation type",
            enum=["add", "subtract", "multiply"],
        )
        assert param.enum == ["add", "subtract", "multiply"]


class TestToolSchema:
    """Tests for ToolSchema dataclass."""

    def test_create_schema(self):
        """Test creating a tool schema."""
        schema = ToolSchema(
            name="search",
            description="Search for items",
            parameters=[
                ToolParameter(name="query", description="Search query"),
            ],
        )
        assert schema.name == "search"
        assert schema.description == "Search for items"
        assert len(schema.parameters) == 1

    def test_schema_defaults(self):
        """Test schema default values."""
        schema = ToolSchema(name="test", description="Test tool")
        assert schema.parameters == []


class TestFunctionTool:
    """Tests for FunctionTool class."""

    def test_create_function_tool(self):
        """Test creating a function tool."""

        def greet(name: str) -> str:
            """Greet a person."""
            return f"Hello, {name}!"

        tool = FunctionTool(greet)
        assert tool.name == "greet"
        assert "Greet a person" in tool.description

    def test_function_tool_with_custom_name(self):
        """Test function tool with custom name."""

        def my_func():
            pass

        tool = FunctionTool(my_func, name="custom_name")
        assert tool.name == "custom_name"

    def test_function_tool_with_custom_description(self):
        """Test function tool with custom description."""

        def my_func():
            pass

        tool = FunctionTool(my_func, description="Custom description")
        assert tool.description == "Custom description"

    def test_function_tool_execute(self):
        """Test executing a function tool."""

        def add(a: int, b: int) -> int:
            """Add two numbers."""
            return a + b

        tool = FunctionTool(add)
        result = tool.execute(a=5, b=3)
        assert result == 8

    def test_auto_parameter_generation(self):
        """Test automatic parameter generation from signature."""

        def process(name: str, count: int, active: bool = True) -> str:
            """Process data."""
            return f"{name}: {count}, active={active}"

        tool = FunctionTool(process)
        params = {p.name: p for p in tool.schema.parameters}

        assert "name" in params
        assert "count" in params
        assert "active" in params

        assert params["name"].required is True
        assert params["count"].required is True
        assert params["active"].required is False
        assert params["active"].default is True

    def test_parameter_type_detection(self):
        """Test parameter type detection."""

        def typed_func(
            s: str,
            i: int,
            f: float,
            b: bool,
            l: list,
            d: dict,
        ):
            pass

        tool = FunctionTool(typed_func)
        params = {p.name: p for p in tool.schema.parameters}

        assert params["s"].param_type == ParameterType.STRING
        assert params["i"].param_type == ParameterType.INTEGER
        assert params["f"].param_type == ParameterType.NUMBER
        assert params["b"].param_type == ParameterType.BOOLEAN
        assert params["l"].param_type == ParameterType.ARRAY
        assert params["d"].param_type == ParameterType.OBJECT


class TestToolDecorator:
    """Tests for @tool decorator."""

    def test_tool_decorator_basic(self):
        """Test basic tool decorator usage."""

        @tool()
        def greet(name: str) -> str:
            """Greet someone."""
            return f"Hello, {name}!"

        assert isinstance(greet, FunctionTool)
        assert greet.name == "greet"

    def test_tool_decorator_with_name(self):
        """Test tool decorator with custom name."""

        @tool(name="greeting")
        def greet(name: str) -> str:
            return f"Hello, {name}!"

        assert greet.name == "greeting"

    def test_tool_decorator_with_description(self):
        """Test tool decorator with custom description."""

        @tool(description="Say hello to someone")
        def greet(name: str) -> str:
            return f"Hello, {name}!"

        assert greet.description == "Say hello to someone"

    def test_decorated_tool_execute(self):
        """Test executing a decorated tool."""

        @tool()
        def multiply(a: int, b: int) -> int:
            """Multiply two numbers."""
            return a * b

        result = multiply.execute(a=4, b=5)
        assert result == 20


class TestToolRegistry:
    """Tests for ToolRegistry class."""

    def test_create_empty_registry(self):
        """Test creating an empty registry."""
        registry = ToolRegistry()
        assert len(registry) == 0

    def test_register_tool(self):
        """Test registering a tool."""

        def greet(name: str) -> str:
            return f"Hello, {name}!"

        registry = ToolRegistry()
        registry.register(greet)

        assert "greet" in registry
        assert len(registry) == 1

    def test_register_function_tool(self):
        """Test registering a FunctionTool."""

        def greet(name: str) -> str:
            return f"Hello, {name}!"

        tool = FunctionTool(greet)
        registry = ToolRegistry()
        registry.register(tool)

        assert "greet" in registry

    def test_register_duplicate_raises_error(self):
        """Test registering duplicate tool raises error."""

        def greet(name: str) -> str:
            return f"Hello, {name}!"

        registry = ToolRegistry()
        registry.register(greet)

        with pytest.raises(ValueError) as exc_info:
            registry.register(greet)

        assert "already registered" in str(exc_info.value)

    def test_unregister_tool(self):
        """Test unregistering a tool."""

        def greet(name: str) -> str:
            return f"Hello, {name}!"

        registry = ToolRegistry()
        registry.register(greet)
        registry.unregister("greet")

        assert "greet" not in registry

    def test_unregister_unknown_raises_error(self):
        """Test unregistering unknown tool raises error."""
        registry = ToolRegistry()

        with pytest.raises(KeyError):
            registry.unregister("unknown")

    def test_get_tool(self):
        """Test getting a tool by name."""

        def greet(name: str) -> str:
            return f"Hello, {name}!"

        registry = ToolRegistry()
        registry.register(greet)

        tool = registry.get("greet")
        assert tool is not None
        assert tool.name == "greet"

    def test_get_unknown_returns_none(self):
        """Test getting unknown tool returns None."""
        registry = ToolRegistry()
        assert registry.get("unknown") is None

    def test_execute_tool(self):
        """Test executing a tool by name."""

        def add(a: int, b: int) -> int:
            return a + b

        registry = ToolRegistry()
        registry.register(add)

        result = registry.execute("add", a=5, b=3)
        assert result == 8

    def test_execute_unknown_raises_error(self):
        """Test executing unknown tool raises error."""
        registry = ToolRegistry()

        with pytest.raises(KeyError):
            registry.execute("unknown")

    def test_list_tools(self):
        """Test listing registered tools."""

        def tool1():
            pass

        def tool2():
            pass

        registry = ToolRegistry()
        registry.register(tool1)
        registry.register(tool2)

        tools = registry.list_tools()
        assert "tool1" in tools
        assert "tool2" in tools

    def test_get_schemas(self):
        """Test getting schemas for all tools."""

        def greet(name: str) -> str:
            """Greet someone."""
            return f"Hello, {name}!"

        registry = ToolRegistry()
        registry.register(greet)

        schemas = registry.get_schemas()
        assert len(schemas) == 1
        assert schemas[0].name == "greet"

    def test_clear_registry(self):
        """Test clearing all tools."""

        def tool1():
            pass

        def tool2():
            pass

        registry = ToolRegistry()
        registry.register(tool1)
        registry.register(tool2)
        registry.clear()

        assert len(registry) == 0

    def test_method_chaining(self):
        """Test method chaining for registry operations."""

        def tool1():
            pass

        def tool2():
            pass

        registry = ToolRegistry().register(tool1).register(tool2)
        assert len(registry) == 2


class TestOpenAIFunctionSchema:
    """Tests for OpenAI function calling schema generation."""

    def test_to_openai_functions_basic(self):
        """Test basic OpenAI function schema generation."""

        def search(query: str) -> list:
            """Search for items."""
            return []

        registry = ToolRegistry()
        registry.register(search)

        functions = registry.to_openai_functions()

        assert len(functions) == 1
        func = functions[0]

        assert func["type"] == "function"
        assert func["function"]["name"] == "search"
        assert "Search for items" in func["function"]["description"]

    def test_openai_function_parameters(self):
        """Test OpenAI function parameters schema."""

        def greet(name: str, formal: bool = False) -> str:
            """Greet a person."""
            return f"Hello, {name}!"

        registry = ToolRegistry()
        registry.register(greet)

        functions = registry.to_openai_functions()
        params = functions[0]["function"]["parameters"]

        assert params["type"] == "object"
        assert "name" in params["properties"]
        assert "formal" in params["properties"]
        assert "name" in params["required"]

    def test_to_openai_tools_alias(self):
        """Test to_openai_tools is alias for to_openai_functions."""

        def test_func():
            pass

        registry = ToolRegistry()
        registry.register(test_func)

        assert registry.to_openai_tools() == registry.to_openai_functions()

    def test_openai_schema_with_enum(self):
        """Test OpenAI schema with enum parameters."""

        @tool()
        def operation(op: str) -> float:
            """Perform an operation."""
            pass

        # Override parameters with enum
        operation._parameters = [
            ToolParameter(
                name="op",
                param_type=ParameterType.STRING,
                description="Operation type",
                enum=["add", "subtract"],
            )
        ]

        registry = ToolRegistry()
        registry.register(operation)

        functions = registry.to_openai_functions()
        props = functions[0]["function"]["parameters"]["properties"]

        assert props["op"]["enum"] == ["add", "subtract"]


class TestBuiltInTools:
    """Tests for built-in coding tools."""

    def test_read_file_tool(self):
        """Test ReadFileTool."""
        tool = ReadFileTool()
        assert tool.name == "read_file"

        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("Hello, World!")
            temp_path = f.name

        try:
            content = tool.execute(path=temp_path)
            assert content == "Hello, World!"
        finally:
            os.unlink(temp_path)

    def test_read_file_not_found(self):
        """Test ReadFileTool with non-existent file."""
        tool = ReadFileTool()

        with pytest.raises(FileNotFoundError):
            tool.execute(path="/nonexistent/file.txt")

    def test_write_file_tool(self):
        """Test WriteFileTool."""
        tool = WriteFileTool()
        assert tool.name == "write_file"

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            temp_path = f.name

        try:
            result = tool.execute(path=temp_path, content="Test content")
            assert result is True

            with open(temp_path, "r") as f:
                assert f.read() == "Test content"
        finally:
            os.unlink(temp_path)

    def test_execute_code_tool(self):
        """Test ExecuteCodeTool."""
        tool = ExecuteCodeTool()
        assert tool.name == "execute_code"

        result = tool.execute(code="result = 2 + 2")
        assert result == 4

    @pytest.mark.parametrize("code,expected_pattern", [
        ("import os", "import statement"),
        ("import sys", "import statement"),
        ("from os import path", "import statement"),
        ("__import__('os')", "__import__"),
        ("exec('print(1)')", "exec()"),
        ("eval('1+1')", "eval()"),
        ("compile('x=1', 'test', 'exec')", "compile()"),
        ("open('/etc/passwd')", "open()"),
        ("open('file.txt', 'r')", "open()"),
        ("file('data.txt')", "file()"),
        ("x.__builtins__", "__builtins__"),
        ("obj.__class__", "__class__"),
        ("cls.__bases__", "__bases__"),
        ("type.__subclasses__()", "__subclasses__"),
        ("globals()", "globals()"),
        ("locals()", "locals()"),
        ("getattr(obj, 'attr')", "getattr()"),
        ("setattr(obj, 'x', 1)", "setattr()"),
        ("delattr(obj, 'x')", "delattr()"),
    ])
    def test_execute_code_tool_blocks_dangerous_patterns(self, code, expected_pattern):
        """Test ExecuteCodeTool blocks dangerous code patterns."""
        tool = ExecuteCodeTool()

        with pytest.raises(ValueError) as exc_info:
            tool.execute(code=code)
        error_msg = str(exc_info.value).lower()
        assert "dangerous" in error_msg, f"Expected 'dangerous' in error message for pattern: {expected_pattern}"
        assert expected_pattern.lower() in error_msg or "pattern" in error_msg, \
            f"Expected pattern '{expected_pattern}' to be mentioned in error message"

    def test_execute_code_tool_unsafe_mode(self):
        """Test ExecuteCodeTool in unsafe mode."""
        tool = ExecuteCodeTool(allow_unsafe=True)
        # In unsafe mode, dangerous patterns are allowed
        result = tool.execute(code="result = len([1, 2, 3])")
        assert result == 3

    def test_search_code_tool(self):
        """Test SearchCodeTool."""
        tool = SearchCodeTool()
        assert tool.name == "search_code"

        # Create a temporary directory with test files
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test.py")
            with open(test_file, "w") as f:
                f.write("def main():\n    print('hello')\n")

            results = tool.execute(
                pattern="def main",
                directory=temp_dir,
                extensions=[".py"],
            )

            assert len(results) > 0
            assert results[0]["line"] == 1
            assert "def main" in results[0]["content"]


class TestCreateDefaultRegistry:
    """Tests for create_default_registry function."""

    def test_create_default_registry(self):
        """Test creating default registry with built-in tools."""
        registry = create_default_registry()

        assert "read_file" in registry
        assert "write_file" in registry
        assert "execute_code" in registry
        assert "search_code" in registry

    def test_default_registry_tools_work(self):
        """Test that default registry tools are functional."""
        registry = create_default_registry()

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            f.write("Test content")
            temp_path = f.name

        try:
            content = registry.execute("read_file", path=temp_path)
            assert content == "Test content"
        finally:
            os.unlink(temp_path)


class TestToolValidation:
    """Tests for tool parameter validation."""

    def test_validate_required_parameters(self):
        """Test validation of required parameters."""

        class CustomTool(Tool):
            def __init__(self):
                super().__init__(
                    name="custom",
                    description="Custom tool",
                    parameters=[
                        ToolParameter(
                            name="required_param",
                            param_type=ParameterType.STRING,
                            required=True,
                        ),
                    ],
                )

            def execute(self, **kwargs):
                self.validate_parameters(**kwargs)
                return True

        tool = CustomTool()

        with pytest.raises(ValueError) as exc_info:
            tool.execute()

        assert "required_param" in str(exc_info.value)

    def test_validate_with_default(self):
        """Test validation passes with defaults."""

        class CustomTool(Tool):
            def __init__(self):
                super().__init__(
                    name="custom",
                    description="Custom tool",
                    parameters=[
                        ToolParameter(
                            name="optional_param",
                            param_type=ParameterType.STRING,
                            required=False,
                            default="default_value",
                        ),
                    ],
                )

            def execute(self, **kwargs):
                self.validate_parameters(**kwargs)
                return True

        tool = CustomTool()
        assert tool.execute() is True
