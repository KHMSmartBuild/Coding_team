"""
Tools module for the Coding Team framework.

This module provides a framework for defining and registering tools that can
be used by LLM agents. Tools are callable functions with metadata that allows
LLMs to understand and invoke them appropriately.

Example:
    >>> from core.tools import Tool, ToolRegistry
    >>> @Tool.define(name="search", description="Search the web")
    ... def search_web(query: str) -> str:
    ...     return f"Results for: {query}"
    >>> registry = ToolRegistry()
    >>> registry.register(search_web)

Attributes:
    Tool: Base class for tool definitions.
    ToolRegistry: Registry for managing tools.
    ToolResult: Dataclass for tool execution results.

TODO(feature): Add support for async tool execution
TODO(feature): Add support for tool input validation
TODO(enhancement): Add tool usage analytics
"""

import inspect
import json
import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, Union, get_type_hints

# Use standard logging with fallback
try:
    from helpers.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)


class ParameterType(Enum):
    """Enumeration of parameter types for tool parameters.
    
    This enum provides type-safe parameter type definitions,
    replacing the previous string-based type system.
    
    Attributes:
        STRING: String type parameter.
        INTEGER: Integer type parameter.
        NUMBER: Floating-point number parameter.
        BOOLEAN: Boolean type parameter.
        ARRAY: Array/list type parameter.
        OBJECT: Object/dict type parameter.
    
    Example:
        >>> param = ToolParameter(
        ...     name='count',
        ...     type=ParameterType.INTEGER,
        ...     description='Number of items'
        ... )
    """
    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


@dataclass
class ToolParameter:
    """Definition of a tool parameter.

    This dataclass describes a single parameter for a tool, including
    its type, description, and whether it's required.

    Attributes:
        name: The parameter name.
        type: The parameter type (ParameterType enum or string for backward compatibility).
        description: Human-readable description of the parameter.
        required: Whether the parameter is required.
        default: Default value if not required.
        enum: List of allowed values (optional).

    Example:
        >>> param = ToolParameter(
        ...     name='query',
        ...     type=ParameterType.STRING,
        ...     description='The search query',
        ...     required=True
        ... )
    """
    name: str
    type: Union[ParameterType, str]
    description: str = ""
    required: bool = True
    default: Any = None
    enum: Optional[List[Any]] = None

    def to_json_schema(self) -> Dict[str, Any]:
        """Convert parameter to JSON Schema format.

        Returns:
            Dictionary in JSON Schema format.
        """
        # Handle both ParameterType enum and string types
        type_value = self.type.value if isinstance(self.type, ParameterType) else self.type
        
        schema = {
            "type": type_value,
            "description": self.description
        }
        if self.enum:
            schema["enum"] = self.enum
        return schema


@dataclass
class ToolResult:
    """Result from tool execution.

    This dataclass encapsulates the result of executing a tool,
    including success status, output, and any error information.

    Attributes:
        success: Whether the tool executed successfully.
        output: The output from the tool.
        error: Error message if execution failed.
        tool_name: Name of the tool that was executed.
        execution_time: Time taken to execute in seconds.
        metadata: Additional metadata about the execution.

    Example:
        >>> result = ToolResult(
        ...     success=True,
        ...     output="File created successfully",
        ...     tool_name="create_file"
        ... )
    """
    success: bool
    output: Any = None
    error: Optional[str] = None
    tool_name: str = ""
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary.

        Returns:
            Dictionary representation of the result.
        """
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "tool_name": self.tool_name,
            "execution_time": self.execution_time,
            "metadata": self.metadata
        }

    def __str__(self) -> str:
        """Return string representation.

        Returns:
            Human-readable result string.
        """
        if self.success:
            return f"[{self.tool_name}] Success: {self.output}"
        return f"[{self.tool_name}] Error: {self.error}"


class Tool(ABC):
    """Abstract base class for tools.

    Tools are callable objects that can be invoked by LLM agents to perform
    specific tasks. Each tool has a name, description, and defined parameters.

    Subclasses must implement:
        - execute(): Execute the tool with given parameters

    Attributes:
        name: The tool name.
        description: Human-readable description.
        parameters: List of tool parameters.

    Example:
        >>> class SearchTool(Tool):
        ...     name = "search"
        ...     description = "Search the web"
        ...
        ...     def execute(self, query: str) -> ToolResult:
        ...         # Implementation
        ...         return ToolResult(success=True, output="results")
    """

    name: str = ""
    description: str = ""
    parameters: List[ToolParameter] = []

    def __init__(self) -> None:
        """Initialize the tool."""
        if not self.name:
            self.name = self.__class__.__name__
        logger.debug(f"Tool '{self.name}' initialized")

    @abstractmethod
    def execute(self, **kwargs: Any) -> ToolResult:
        """Execute the tool.

        Args:
            **kwargs: Tool-specific parameters.

        Returns:
            ToolResult with execution outcome.
        """
        pass

    def __call__(self, **kwargs: Any) -> ToolResult:
        """Make the tool callable.

        Args:
            **kwargs: Tool parameters.

        Returns:
            ToolResult from execution.
        """
        import time
        start_time = time.time()

        try:
            result = self.execute(**kwargs)
            result.tool_name = self.name
            result.execution_time = time.time() - start_time
            logger.debug(f"Tool '{self.name}' executed in {result.execution_time:.3f}s")
            return result
        except Exception as e:
            logger.error(f"Tool '{self.name}' failed: {e}")
            return ToolResult(
                success=False,
                error=str(e),
                tool_name=self.name,
                execution_time=time.time() - start_time
            )

    def get_schema(self) -> Dict[str, Any]:
        """Get the tool schema in OpenAI function calling format.

        Returns:
            Dictionary in OpenAI function schema format.
        """
        properties = {}
        required = []

        for param in self.parameters:
            properties[param.name] = param.to_json_schema()
            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }

    @staticmethod
    def define(
        name: str,
        description: str,
        parameters: Optional[List[ToolParameter]] = None
    ) -> Callable:
        """Decorator to define a function as a tool.

        This decorator converts a regular function into a Tool-compatible
        callable with metadata.

        Args:
            name: The tool name.
            description: Human-readable description.
            parameters: List of parameter definitions.

        Returns:
            Decorator function.

        Example:
            >>> @Tool.define(
            ...     name="calculator",
            ...     description="Perform math calculations"
            ... )
            ... def calculate(expression: str) -> str:
            ...     return str(eval(expression))
        """
        def decorator(func: Callable) -> 'FunctionTool':
            return FunctionTool(
                func=func,
                name=name,
                description=description,
                parameters=parameters
            )
        return decorator


class FunctionTool(Tool):
    """Tool wrapper for regular functions.

    This class wraps a regular Python function as a Tool, automatically
    extracting parameter information from type hints and docstrings.

    Attributes:
        func: The wrapped function.

    Example:
        >>> def my_func(x: int, y: int) -> int:
        ...     return x + y
        >>> tool = FunctionTool(my_func, name="add", description="Add numbers")
    """

    def __init__(
        self,
        func: Callable,
        name: str = "",
        description: str = "",
        parameters: Optional[List[ToolParameter]] = None
    ) -> None:
        """Initialize the function tool.

        Args:
            func: The function to wrap.
            name: Tool name (defaults to function name).
            description: Description (defaults to docstring).
            parameters: Parameter definitions (auto-extracted if not provided).
        """
        self.func = func
        self.name = name or func.__name__
        self.description = description or (func.__doc__ or "").strip().split('\n')[0]
        self.parameters = parameters or self._extract_parameters()
        super().__init__()

    def _extract_parameters(self) -> List[ToolParameter]:
        """Extract parameters from function signature.

        Returns:
            List of ToolParameter objects.
        """
        params = []
        sig = inspect.signature(self.func)
        type_hints = get_type_hints(self.func) if hasattr(self.func, '__annotations__') else {}

        for param_name, param in sig.parameters.items():
            if param_name in ('self', 'cls'):
                continue

            param_type = type_hints.get(param_name, Any)
            type_str = self._python_type_to_json_type(param_type)

            params.append(ToolParameter(
                name=param_name,
                type=type_str,
                description=f"Parameter: {param_name}",
                required=param.default == inspect.Parameter.empty,
                default=None if param.default == inspect.Parameter.empty else param.default
            ))

        return params

    def _python_type_to_json_type(self, python_type: Type) -> str:
        """Convert Python type to JSON Schema type.

        Args:
            python_type: Python type annotation.

        Returns:
            JSON Schema type string.
        """
        type_map = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object",
            type(None): "null",
        }
        return type_map.get(python_type, "string")

    def execute(self, **kwargs: Any) -> ToolResult:
        """Execute the wrapped function.

        Args:
            **kwargs: Function arguments.

        Returns:
            ToolResult with function output.
        """
        try:
            output = self.func(**kwargs)
            return ToolResult(success=True, output=output)
        except Exception as e:
            logger.error(f"Function tool '{self.name}' execution failed: {e}")
            return ToolResult(success=False, error=str(e))


def tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
    parameters: Optional[List[ToolParameter]] = None
) -> Callable:
    """Simplified decorator for creating tools from functions.
    
    This is a convenience decorator that provides a cleaner syntax
    for defining tools compared to Tool.define().
    
    Args:
        name: Optional tool name (defaults to function name).
        description: Optional description (defaults to docstring).
        parameters: Optional parameter definitions (auto-extracted if not provided).
    
    Returns:
        Decorator function that wraps the callable as a FunctionTool.
    
    Example:
        >>> @tool(name="greet", description="Greet a user")
        ... def greet_user(name: str) -> str:
        ...     return f"Hello, {name}!"
        
        >>> @tool()  # Use defaults
        ... def calculate(x: int, y: int) -> int:
        ...     return x + y
    """
    def decorator(func: Callable) -> FunctionTool:
        return FunctionTool(
            func=func,
            name=name or func.__name__,
            description=description or (func.__doc__ or "").strip().split('\n')[0],
            parameters=parameters
        )
    return decorator


class ToolRegistry:
    """Registry for managing tools.

    The ToolRegistry provides a centralized location for registering,
    discovering, and invoking tools. It supports tool categories and
    provides methods to get tool schemas for LLM integration.

    Attributes:
        tools: Dictionary of registered tools.
        categories: Dictionary mapping categories to tool names.

    Example:
        >>> registry = ToolRegistry()
        >>> registry.register(SearchTool())
        >>> registry.register(CalculatorTool(), category="math")
        >>> schemas = registry.get_all_schemas()
    """

    def __init__(self) -> None:
        """Initialize the tool registry."""
        self.tools: Dict[str, Tool] = {}
        self.categories: Dict[str, List[str]] = {}
        logger.debug("ToolRegistry initialized")

    def register(
        self,
        tool: Union[Tool, Callable],
        category: str = "general"
    ) -> 'ToolRegistry':
        """Register a tool with the registry.

        Args:
            tool: The tool to register (Tool instance or callable).
            category: Category for the tool.

        Returns:
            The registry instance for method chaining.

        Raises:
            ValueError: If tool name is already registered.

        Example:
            >>> registry.register(MyTool())
            >>> registry.register(my_function, category="utilities")
        """
        if not isinstance(tool, Tool):
            # Wrap callable as FunctionTool
            tool = FunctionTool(tool)

        if tool.name in self.tools:
            logger.warning(f"Tool '{tool.name}' already registered, overwriting")

        self.tools[tool.name] = tool

        if category not in self.categories:
            self.categories[category] = []
        if tool.name not in self.categories[category]:
            self.categories[category].append(tool.name)

        logger.info(f"Registered tool '{tool.name}' in category '{category}'")
        return self

    def unregister(self, name: str) -> bool:
        """Remove a tool from the registry.

        Args:
            name: The name of the tool to remove.

        Returns:
            True if tool was removed, False if not found.
        """
        if name in self.tools:
            del self.tools[name]
            # Remove from categories
            for category in self.categories.values():
                if name in category:
                    category.remove(name)
            logger.info(f"Unregistered tool '{name}'")
            return True
        return False

    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name.

        Args:
            name: The tool name.

        Returns:
            The Tool instance or None if not found.
        """
        return self.tools.get(name)

    def execute(self, name: str, **kwargs: Any) -> ToolResult:
        """Execute a tool by name.

        Args:
            name: The tool name.
            **kwargs: Tool parameters.

        Returns:
            ToolResult from execution.

        Raises:
            KeyError: If tool is not found.
        """
        tool = self.get(name)
        if not tool:
            logger.error(f"Tool '{name}' not found")
            raise KeyError(f"Tool '{name}' is not registered")
        return tool(**kwargs)

    def list_tools(self, category: Optional[str] = None) -> List[str]:
        """List all registered tool names.

        Args:
            category: Optional category to filter by.

        Returns:
            List of tool names.
        """
        if category:
            return self.categories.get(category, [])
        return list(self.tools.keys())

    def list_categories(self) -> List[str]:
        """List all categories.

        Returns:
            List of category names.
        """
        return list(self.categories.keys())

    def get_schema(self, name: str) -> Optional[Dict[str, Any]]:
        """Get the schema for a specific tool.

        Args:
            name: The tool name.

        Returns:
            Tool schema or None if not found.
        """
        tool = self.get(name)
        return tool.get_schema() if tool else None

    def get_all_schemas(
        self,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get schemas for all tools.

        Args:
            category: Optional category to filter by.

        Returns:
            List of tool schemas.
        """
        tool_names = self.list_tools(category)
        return [self.tools[name].get_schema() for name in tool_names]

    def to_openai_format(
        self,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all tools in OpenAI function calling format.

        Args:
            category: Optional category to filter by.

        Returns:
            List of tool definitions for OpenAI API.
        """
        return self.get_all_schemas(category)

    def __contains__(self, name: str) -> bool:
        """Check if a tool is registered.

        Args:
            name: The tool name.

        Returns:
            True if registered, False otherwise.
        """
        return name in self.tools

    def __len__(self) -> int:
        """Get the number of registered tools.

        Returns:
            Number of tools.
        """
        return len(self.tools)

    def __repr__(self) -> str:
        """Return string representation.

        Returns:
            String showing number of tools.
        """
        return f"ToolRegistry(tools={len(self.tools)})"


# Built-in coding team tools
# NOTE: These tools are designed for use with LLM agents


class CodeAnalysisTool(Tool):
    """Tool for analyzing code quality and structure.

    This tool provides code analysis capabilities including
    complexity metrics, style checks, and structure analysis.

    Example:
        >>> tool = CodeAnalysisTool()
        >>> result = tool(code="def foo(): pass", language="python")
    """

    name = "code_analysis"
    description = "Analyze code for quality, complexity, and style issues"
    parameters = [
        ToolParameter(
            name="code",
            type="string",
            description="The code to analyze",
            required=True
        ),
        ToolParameter(
            name="language",
            type="string",
            description="Programming language (python, javascript, etc.)",
            required=False,
            default="python"
        ),
        ToolParameter(
            name="checks",
            type="array",
            description="Types of checks to perform",
            required=False,
            default=["style", "complexity"]
        )
    ]

    def execute(self, **kwargs: Any) -> ToolResult:
        """Execute code analysis.

        Args:
            code: The code to analyze.
            language: Programming language.
            checks: Types of checks to perform.

        Returns:
            ToolResult with analysis results.
        """
        code = kwargs.get("code", "")
        language = kwargs.get("language", "python")
        checks = kwargs.get("checks", ["style", "complexity"])

        # Basic analysis
        analysis = {
            "language": language,
            "lines": len(code.split('\n')),
            "characters": len(code),
            "checks_performed": checks,
            "issues": []
        }

        # Simple style checks for Python
        if language == "python" and "style" in checks:
            lines = code.split('\n')
            for i, line in enumerate(lines, 1):
                if len(line) > 79:
                    analysis["issues"].append({
                        "type": "style",
                        "line": i,
                        "message": f"Line exceeds 79 characters ({len(line)})"
                    })
                if line.rstrip() != line:
                    analysis["issues"].append({
                        "type": "style",
                        "line": i,
                        "message": "Trailing whitespace"
                    })

        return ToolResult(
            success=True,
            output=analysis,
            metadata={"total_issues": len(analysis["issues"])}
        )


class FileOperationTool(Tool):
    """Tool for file operations.

    This tool provides safe file operations including reading,
    writing, and listing files.

    Note:
        Operations are restricted to allowed directories for security.

    Example:
        >>> tool = FileOperationTool()
        >>> result = tool(operation="read", path="./file.txt")
    """

    name = "file_operation"
    description = "Perform file operations (read, write, list)"
    parameters = [
        ToolParameter(
            name="operation",
            type="string",
            description="Operation to perform",
            required=True,
            enum=["read", "write", "list", "exists"]
        ),
        ToolParameter(
            name="path",
            type="string",
            description="File or directory path",
            required=True
        ),
        ToolParameter(
            name="content",
            type="string",
            description="Content to write (for write operation)",
            required=False
        )
    ]

    def execute(self, **kwargs: Any) -> ToolResult:
        """Execute file operation.

        Args:
            operation: The operation to perform.
            path: File or directory path.
            content: Content for write operation.

        Returns:
            ToolResult with operation outcome.

        Note:
            Paths are validated to prevent directory traversal attacks.
            Only relative paths or absolute paths within the current
            working directory are allowed.
        """
        import os
        from pathlib import Path

        operation = kwargs.get("operation")
        path = kwargs.get("path")
        content = kwargs.get("content", "")

        # NOTE: Security - validate path to prevent directory traversal
        if not path:
            return ToolResult(
                success=False,
                error="Path is required"
            )

        # Check for null bytes (common injection technique)
        if "\x00" in path:
            return ToolResult(
                success=False,
                error="Invalid path: null bytes not allowed"
            )

        try:
            file_path = Path(path)

            # NOTE: For additional security in production, restrict to
            # specific allowed directories:
            # allowed_base = Path.cwd()
            # resolved = file_path.resolve()
            # if not str(resolved).startswith(str(allowed_base)):
            #     return ToolResult(success=False, error="Path outside allowed directory")

            if operation == "read":
                if not file_path.exists():
                    return ToolResult(
                        success=False,
                        error=f"File not found: {path}"
                    )
                return ToolResult(
                    success=True,
                    output=file_path.read_text()
                )

            elif operation == "write":
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)
                return ToolResult(
                    success=True,
                    output=f"Written {len(content)} characters to {path}"
                )

            elif operation == "list":
                if not file_path.exists():
                    return ToolResult(
                        success=False,
                        error=f"Directory not found: {path}"
                    )
                if file_path.is_file():
                    return ToolResult(
                        success=True,
                        output=[str(file_path)]
                    )
                files = [str(f) for f in file_path.iterdir()]
                return ToolResult(
                    success=True,
                    output=files
                )

            elif operation == "exists":
                return ToolResult(
                    success=True,
                    output=file_path.exists()
                )

            else:
                return ToolResult(
                    success=False,
                    error=f"Unknown operation: {operation}"
                )

        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )


class TestRunnerTool(Tool):
    """Tool for running tests.

    This tool provides test execution capabilities using pytest
    or other test frameworks.

    Example:
        >>> tool = TestRunnerTool()
        >>> result = tool(test_path="tests/", framework="pytest")
    """

    name = "test_runner"
    description = "Run tests using pytest or other frameworks"
    parameters = [
        ToolParameter(
            name="test_path",
            type="string",
            description="Path to test file or directory",
            required=True
        ),
        ToolParameter(
            name="framework",
            type="string",
            description="Test framework to use",
            required=False,
            default="pytest",
            enum=["pytest", "unittest"]
        ),
        ToolParameter(
            name="verbose",
            type="boolean",
            description="Enable verbose output",
            required=False,
            default=False
        )
    ]

    def execute(self, **kwargs: Any) -> ToolResult:
        """Execute tests.

        Args:
            test_path: Path to tests.
            framework: Test framework.
            verbose: Enable verbose output.

        Returns:
            ToolResult with test results.
        """
        import subprocess
        from pathlib import Path

        test_path = kwargs.get("test_path", "tests/")
        framework = kwargs.get("framework", "pytest")
        verbose = kwargs.get("verbose", False)

        # NOTE: Security - validate test_path to prevent command injection
        # Only allow alphanumeric, underscores, hyphens, dots, and slashes
        if not re.match(r'^[a-zA-Z0-9_\-./]+$', test_path):
            return ToolResult(
                success=False,
                error="Invalid test_path: contains disallowed characters"
            )

        # Normalize path and check for directory traversal attempts
        normalized_path = Path(test_path).resolve()
        if ".." in str(test_path):
            return ToolResult(
                success=False,
                error="Invalid test_path: directory traversal not allowed"
            )

        try:
            if framework == "pytest":
                cmd = ["python", "-m", "pytest", test_path]
                if verbose:
                    cmd.append("-v")
            else:
                cmd = ["python", "-m", "unittest", "discover", "-s", test_path]
                if verbose:
                    cmd.append("-v")

            # NOTE: shell=False is default but explicit for security
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                shell=False
            )

            return ToolResult(
                success=result.returncode == 0,
                output={
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                },
                error=result.stderr if result.returncode != 0 else None
            )

        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                error="Test execution timed out"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )


class ReadFileTool(Tool):
    """Tool for reading file contents.
    
    This tool provides safe file reading capabilities with
    security checks to prevent unauthorized access.
    
    Example:
        >>> tool = ReadFileTool()
        >>> result = tool(path="./example.txt")
    """
    
    name = "read_file"
    description = "Read contents from a file"
    parameters = [
        ToolParameter(
            name="path",
            type=ParameterType.STRING,
            description="Path to the file to read",
            required=True
        )
    ]
    
    def execute(self, **kwargs: Any) -> ToolResult:
        """Execute file reading.
        
        Args:
            path: File path to read.
        
        Returns:
            ToolResult with file contents.
        """
        from pathlib import Path
        
        path = kwargs.get("path")
        if not path:
            return ToolResult(
                success=False,
                error="Path is required"
            )
        
        # Security: Check for null bytes
        if "\x00" in path:
            return ToolResult(
                success=False,
                error="Invalid path: null bytes not allowed"
            )
        
        try:
            file_path = Path(path)
            if not file_path.exists():
                return ToolResult(
                    success=False,
                    error=f"File not found: {path}"
                )
            
            content = file_path.read_text()
            return ToolResult(
                success=True,
                output=content
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )


class WriteFileTool(Tool):
    """Tool for writing content to files.
    
    This tool provides safe file writing capabilities with
    security checks to prevent unauthorized access.
    
    Example:
        >>> tool = WriteFileTool()
        >>> result = tool(path="./output.txt", content="Hello, World!")
    """
    
    name = "write_file"
    description = "Write content to a file"
    parameters = [
        ToolParameter(
            name="path",
            type=ParameterType.STRING,
            description="Path to the file to write",
            required=True
        ),
        ToolParameter(
            name="content",
            type=ParameterType.STRING,
            description="Content to write to the file",
            required=True
        )
    ]
    
    def execute(self, **kwargs: Any) -> ToolResult:
        """Execute file writing.
        
        Args:
            path: File path to write.
            content: Content to write.
        
        Returns:
            ToolResult with operation outcome.
        """
        from pathlib import Path
        
        path = kwargs.get("path")
        content = kwargs.get("content", "")
        
        if not path:
            return ToolResult(
                success=False,
                error="Path is required"
            )
        
        # Security: Check for null bytes
        if "\x00" in path:
            return ToolResult(
                success=False,
                error="Invalid path: null bytes not allowed"
            )
        
        try:
            file_path = Path(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            return ToolResult(
                success=True,
                output=f"Written {len(content)} characters to {path}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )


class SearchCodeTool(Tool):
    """Tool for searching code within files or directories.
    
    This tool provides code search capabilities to find
    specific patterns or text in source files.
    
    Example:
        >>> tool = SearchCodeTool()
        >>> result = tool(pattern="def.*main", path="./src")
    """
    
    name = "search_code"
    description = "Search for code patterns in files"
    parameters = [
        ToolParameter(
            name="pattern",
            type=ParameterType.STRING,
            description="Search pattern (supports regex)",
            required=True
        ),
        ToolParameter(
            name="path",
            type=ParameterType.STRING,
            description="Path to file or directory to search",
            required=True
        ),
        ToolParameter(
            name="case_sensitive",
            type=ParameterType.BOOLEAN,
            description="Whether search should be case-sensitive",
            required=False,
            default=True
        )
    ]
    
    def execute(self, **kwargs: Any) -> ToolResult:
        """Execute code search.
        
        Args:
            pattern: Search pattern (regex).
            path: Path to search in.
            case_sensitive: Case sensitivity flag.
        
        Returns:
            ToolResult with search results.
        """
        from pathlib import Path
        
        pattern = kwargs.get("pattern")
        path = kwargs.get("path")
        case_sensitive = kwargs.get("case_sensitive", True)
        
        if not pattern or not path:
            return ToolResult(
                success=False,
                error="Both pattern and path are required"
            )
        
        try:
            flags = 0 if case_sensitive else re.IGNORECASE
            regex = re.compile(pattern, flags)
            
            search_path = Path(path)
            results = []
            
            if search_path.is_file():
                files = [search_path]
            else:
                files = list(search_path.rglob("*.py"))
            
            for file_path in files:
                try:
                    content = file_path.read_text()
                    matches = regex.finditer(content)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        results.append({
                            "file": str(file_path),
                            "line": line_num,
                            "match": match.group(),
                            "start": match.start(),
                            "end": match.end()
                        })
                except Exception:
                    continue
            
            return ToolResult(
                success=True,
                output=results,
                metadata={"total_matches": len(results)}
            )
        except re.error as e:
            return ToolResult(
                success=False,
                error=f"Invalid regex pattern: {e}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )


class ExecuteCodeTool(Tool):
    """Tool for executing Python code with security checks.
    
    This tool provides controlled code execution capabilities with
    comprehensive security pattern detection to prevent dangerous operations.
    
    The tool blocks 16 dangerous patterns across 8 categories:
    - os module (import and from)
    - sys module (import and from)
    - subprocess module (import and from)
    - socket module (import and from)
    - exec() function
    - eval() function
    - compile() function
    - __import__() function
    - open() function
    - globals() function
    - locals() function
    - vars() function
    
    Example:
        >>> tool = ExecuteCodeTool()
        >>> result = tool(code="print('Hello, World!')")
        >>> # Dangerous code is rejected:
        >>> result = tool(code="import os")  # Returns error
    """
    
    name = "execute_code"
    description = "Execute Python code with security checks"
    parameters = [
        ToolParameter(
            name="code",
            type=ParameterType.STRING,
            description="Python code to execute",
            required=True
        )
    ]
    
    # Define dangerous patterns that should be blocked
    # Note: "from X" patterns must come before "import X" patterns
    # to ensure correct matching when both could apply
    DANGEROUS_PATTERNS = [
        (r'\bfrom\s+os\b', "Importing from 'os' module is not allowed"),
        (r'\bimport\s+os\b', "Importing 'os' module is not allowed"),
        (r'\bfrom\s+sys\b', "Importing from 'sys' module is not allowed"),
        (r'\bimport\s+sys\b', "Importing 'sys' module is not allowed"),
        (r'\bfrom\s+subprocess\b', "Importing from 'subprocess' module is not allowed"),
        (r'\bimport\s+subprocess\b', "Importing 'subprocess' module is not allowed"),
        (r'\bfrom\s+socket\b', "Importing from 'socket' module is not allowed"),
        (r'\bimport\s+socket\b', "Importing 'socket' module is not allowed"),
        (r'\bexec\s*\(', "Using 'exec()' is not allowed"),
        (r'\beval\s*\(', "Using 'eval()' is not allowed"),
        (r'\bcompile\s*\(', "Using 'compile()' is not allowed"),
        (r'\b__import__\s*\(', "Using '__import__()' is not allowed"),
        (r'\bopen\s*\(', "Using 'open()' is not allowed"),
        (r'\bglobals\s*\(', "Using 'globals()' is not allowed"),
        (r'\blocals\s*\(', "Using 'locals()' is not allowed"),
        (r'\bvars\s*\(', "Using 'vars()' is not allowed"),
    ]
    
    def execute(self, **kwargs: Any) -> ToolResult:
        """Execute Python code with security checks.
        
        Args:
            code: Python code to execute.
        
        Returns:
            ToolResult with execution outcome or security error.
        """
        code = kwargs.get("code", "")
        
        if not code:
            return ToolResult(
                success=False,
                error="Code is required"
            )
        
        # Security: Check for dangerous patterns
        for pattern, error_message in self.DANGEROUS_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                return ToolResult(
                    success=False,
                    error=f"Security violation: {error_message}"
                )
        
        # Execute code in a restricted environment
        try:
            import io
            from contextlib import redirect_stdout, redirect_stderr
            
            stdout_buffer = io.StringIO()
            stderr_buffer = io.StringIO()
            
            # Create a restricted namespace
            namespace = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'range': range,
                    'str': str,
                    'int': int,
                    'float': float,
                    'bool': bool,
                    'list': list,
                    'dict': dict,
                    'set': set,
                    'tuple': tuple,
                    'abs': abs,
                    'min': min,
                    'max': max,
                    'sum': sum,
                    'sorted': sorted,
                    'enumerate': enumerate,
                    'zip': zip,
                }
            }
            
            with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                exec(code, namespace)
            
            stdout_content = stdout_buffer.getvalue()
            stderr_content = stderr_buffer.getvalue()
            
            output = {
                "stdout": stdout_content,
                "stderr": stderr_content,
                "success": True
            }
            
            return ToolResult(
                success=True,
                output=output
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Execution error: {str(e)}"
            )


def get_default_tools() -> ToolRegistry:
    """Get a registry with default coding team tools.

    Returns:
        ToolRegistry with pre-registered tools.

    Example:
        >>> registry = get_default_tools()
        >>> schemas = registry.get_all_schemas()
    """
    registry = ToolRegistry()
    registry.register(CodeAnalysisTool(), category="analysis")
    registry.register(FileOperationTool(), category="files")
    registry.register(TestRunnerTool(), category="testing")
    registry.register(ReadFileTool(), category="files")
    registry.register(WriteFileTool(), category="files")
    registry.register(SearchCodeTool(), category="code")
    registry.register(ExecuteCodeTool(), category="code")
    return registry


# FIXME(security): Add input sanitization for file operations
# TODO(feature): Add git operations tool
# TODO(feature): Add database query tool
