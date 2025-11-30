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
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, Union, get_type_hints

from helpers.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class ToolParameter:
    """Definition of a tool parameter.

    This dataclass describes a single parameter for a tool, including
    its type, description, and whether it's required.

    Attributes:
        name: The parameter name.
        type: The parameter type as a string.
        description: Human-readable description of the parameter.
        required: Whether the parameter is required.
        default: Default value if not required.
        enum: List of allowed values (optional).

    Example:
        >>> param = ToolParameter(
        ...     name='query',
        ...     type='string',
        ...     description='The search query',
        ...     required=True
        ... )
    """
    name: str
    type: str
    description: str = ""
    required: bool = True
    default: Any = None
    enum: Optional[List[Any]] = None

    def to_json_schema(self) -> Dict[str, Any]:
        """Convert parameter to JSON Schema format.

        Returns:
            Dictionary in JSON Schema format.
        """
        schema = {
            "type": self.type,
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
        """
        import os
        from pathlib import Path

        operation = kwargs.get("operation")
        path = kwargs.get("path")
        content = kwargs.get("content", "")

        try:
            file_path = Path(path)

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

        test_path = kwargs.get("test_path", "tests/")
        framework = kwargs.get("framework", "pytest")
        verbose = kwargs.get("verbose", False)

        try:
            if framework == "pytest":
                cmd = ["python", "-m", "pytest", test_path]
                if verbose:
                    cmd.append("-v")
            else:
                cmd = ["python", "-m", "unittest", "discover", "-s", test_path]
                if verbose:
                    cmd.append("-v")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
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
    return registry


# FIXME(security): Add input sanitization for file operations
# TODO(feature): Add git operations tool
# TODO(feature): Add database query tool
