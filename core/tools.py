"""
Tools Framework Module.

This module provides a framework for creating and managing tools that can be
used by AI agents. It includes a registry, schema generation for OpenAI
function-calling, and built-in coding tools.

Example:
    >>> @tool(name="greet", description="Greet a person")
    ... def greet(name: str) -> str:
    ...     return f"Hello, {name}!"
    >>> registry.register(greet)
"""

import inspect
import re as regex_module
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union, get_type_hints

T = TypeVar("T")


class ParameterType(Enum):
    """Enumeration of parameter types for tool schemas.

    Attributes:
        STRING: String type.
        INTEGER: Integer type.
        NUMBER: Float/Number type.
        BOOLEAN: Boolean type.
        ARRAY: Array/List type.
        OBJECT: Object/Dict type.
    """

    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


@dataclass
class ToolParameter:
    """Describes a parameter for a tool.

    Attributes:
        name: The parameter name.
        param_type: The parameter type.
        description: Description of the parameter.
        required: Whether the parameter is required.
        default: Default value if not required.
        enum: List of allowed values.
    """

    name: str
    param_type: ParameterType = ParameterType.STRING
    description: str = ""
    required: bool = True
    default: Optional[Any] = None
    enum: Optional[List[str]] = None


@dataclass
class ToolSchema:
    """Schema definition for a tool.

    Attributes:
        name: The tool name.
        description: Description of what the tool does.
        parameters: List of tool parameters.
    """

    name: str
    description: str
    parameters: List[ToolParameter] = field(default_factory=list)


class Tool(ABC):
    """Abstract base class for tools.

    Tools can be executed by AI agents to perform specific tasks.

    Attributes:
        name: The tool name.
        description: Description of the tool.
        schema: The tool schema.

    Example:
        >>> class MyTool(Tool):
        ...     def execute(self, **kwargs):
        ...         return "Result"
    """

    def __init__(
        self,
        name: str,
        description: str,
        parameters: Optional[List[ToolParameter]] = None,
    ):
        """Initialize the tool.

        Args:
            name: The tool name.
            description: Description of the tool.
            parameters: List of tool parameters.
        """
        self.name = name
        self.description = description
        self._parameters = parameters or []

    @property
    def schema(self) -> ToolSchema:
        """Get the tool schema.

        Returns:
            The tool schema.
        """
        return ToolSchema(
            name=self.name,
            description=self.description,
            parameters=self._parameters,
        )

    @abstractmethod
    def execute(self, **kwargs: Any) -> Any:
        """Execute the tool.

        Args:
            **kwargs: Tool-specific arguments.

        Returns:
            The tool execution result.
        """
        pass

    def validate_parameters(self, **kwargs: Any) -> bool:
        """Validate the provided parameters.

        Args:
            **kwargs: Parameters to validate.

        Returns:
            True if valid, raises ValueError otherwise.

        Raises:
            ValueError: If required parameters are missing.
        """
        for param in self._parameters:
            if param.required and param.name not in kwargs:
                if param.default is None:
                    raise ValueError(f"Missing required parameter: {param.name}")
        return True


class FunctionTool(Tool):
    """Tool wrapper for Python functions.

    Wraps a Python function as a tool with automatic schema generation.

    Attributes:
        func: The wrapped function.

    Example:
        >>> def greet(name: str) -> str:
        ...     return f"Hello, {name}!"
        >>> tool = FunctionTool(greet, "greet", "Greet a person")
    """

    def __init__(
        self,
        func: Callable[..., Any],
        name: Optional[str] = None,
        description: Optional[str] = None,
        parameters: Optional[List[ToolParameter]] = None,
    ):
        """Initialize the function tool.

        Args:
            func: The function to wrap.
            name: Optional override for the tool name.
            description: Optional override for the description.
            parameters: Optional override for parameters.
        """
        self.func = func
        tool_name = name or func.__name__
        tool_description = description or func.__doc__ or ""

        # Auto-generate parameters if not provided
        if parameters is None:
            parameters = self._generate_parameters(func)

        super().__init__(tool_name, tool_description.strip(), parameters)

    def _generate_parameters(self, func: Callable[..., Any]) -> List[ToolParameter]:
        """Generate parameters from function signature.

        Args:
            func: The function to analyze.

        Returns:
            List of ToolParameter objects.
        """
        params = []
        sig = inspect.signature(func)
        type_hints = {}
        try:
            type_hints = get_type_hints(func)
        except Exception:
            # Type hints may fail to resolve due to forward references, missing imports,
            # or other issues. Fall back to treating all parameters as strings.
            pass

        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue

            param_type = self._python_type_to_param_type(
                type_hints.get(param_name, str)
            )
            required = param.default is inspect.Parameter.empty
            default = None if required else param.default

            params.append(
                ToolParameter(
                    name=param_name,
                    param_type=param_type,
                    description=f"Parameter: {param_name}",
                    required=required,
                    default=default,
                )
            )

        return params

    def _python_type_to_param_type(self, python_type: type) -> ParameterType:
        """Convert Python type to ParameterType.

        Args:
            python_type: The Python type.

        Returns:
            The corresponding ParameterType.
        """
        type_map = {
            str: ParameterType.STRING,
            int: ParameterType.INTEGER,
            float: ParameterType.NUMBER,
            bool: ParameterType.BOOLEAN,
            list: ParameterType.ARRAY,
            dict: ParameterType.OBJECT,
        }
        return type_map.get(python_type, ParameterType.STRING)

    def execute(self, **kwargs: Any) -> Any:
        """Execute the wrapped function.

        Args:
            **kwargs: Arguments to pass to the function.

        Returns:
            The function result.
        """
        self.validate_parameters(**kwargs)
        return self.func(**kwargs)


def tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> Callable[[Callable[..., T]], FunctionTool]:
    """Decorator to create a FunctionTool from a function.

    Args:
        name: Optional tool name override.
        description: Optional description override.

    Returns:
        A decorator that creates a FunctionTool.

    Example:
        >>> @tool(name="greet", description="Greet someone")
        ... def greet(name: str) -> str:
        ...     return f"Hello, {name}!"
    """

    def decorator(func: Callable[..., T]) -> FunctionTool:
        return FunctionTool(func, name=name, description=description)

    return decorator


class ToolRegistry:
    """Registry for managing tools.

    Provides registration, lookup, and schema generation for tools.

    Attributes:
        _tools: Dictionary of registered tools.

    Example:
        >>> registry = ToolRegistry()
        >>> registry.register(my_tool)
        >>> result = registry.execute("my_tool", arg="value")
    """

    def __init__(self):
        """Initialize the registry."""
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Union[Tool, Callable[..., Any]], **kwargs: Any) -> "ToolRegistry":
        """Register a tool.

        Args:
            tool: The tool to register (Tool instance or callable).
            **kwargs: Additional arguments for FunctionTool creation.

        Returns:
            The registry instance for method chaining.

        Raises:
            ValueError: If a tool with the same name is already registered.
        """
        if callable(tool) and not isinstance(tool, Tool):
            tool = FunctionTool(tool, **kwargs)

        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered")

        self._tools[tool.name] = tool
        return self

    def unregister(self, name: str) -> "ToolRegistry":
        """Unregister a tool.

        Args:
            name: The name of the tool to unregister.

        Returns:
            The registry instance for method chaining.

        Raises:
            KeyError: If the tool is not registered.
        """
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' is not registered")
        del self._tools[name]
        return self

    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name.

        Args:
            name: The tool name.

        Returns:
            The tool if found, None otherwise.
        """
        return self._tools.get(name)

    def execute(self, name: str, **kwargs: Any) -> Any:
        """Execute a tool by name.

        Args:
            name: The tool name.
            **kwargs: Arguments to pass to the tool.

        Returns:
            The tool execution result.

        Raises:
            KeyError: If the tool is not registered.
        """
        tool = self.get(name)
        if tool is None:
            raise KeyError(f"Tool '{name}' is not registered")
        return tool.execute(**kwargs)

    def list_tools(self) -> List[str]:
        """List all registered tool names.

        Returns:
            List of tool names.
        """
        return list(self._tools.keys())

    def get_schemas(self) -> List[ToolSchema]:
        """Get schemas for all registered tools.

        Returns:
            List of tool schemas.
        """
        return [tool.schema for tool in self._tools.values()]

    def to_openai_functions(self) -> List[Dict[str, Any]]:
        """Generate OpenAI function-calling schema.

        Returns:
            List of OpenAI function definitions.

        Example:
            >>> functions = registry.to_openai_functions()
            >>> response = openai.chat.completions.create(
            ...     model="gpt-4",
            ...     functions=functions,
            ...     ...
            ... )
        """
        functions = []
        for tool in self._tools.values():
            func_def = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            }

            for param in tool.schema.parameters:
                prop = {
                    "type": param.param_type.value,
                    "description": param.description,
                }
                if param.enum:
                    prop["enum"] = param.enum

                func_def["function"]["parameters"]["properties"][param.name] = prop

                if param.required:
                    func_def["function"]["parameters"]["required"].append(param.name)

            functions.append(func_def)

        return functions

    def to_openai_tools(self) -> List[Dict[str, Any]]:
        """Alias for to_openai_functions.

        Returns:
            List of OpenAI tool definitions.
        """
        return self.to_openai_functions()

    def clear(self) -> "ToolRegistry":
        """Clear all registered tools.

        Returns:
            The registry instance for method chaining.
        """
        self._tools.clear()
        return self

    def __contains__(self, name: str) -> bool:
        """Check if a tool is registered.

        Args:
            name: The tool name.

        Returns:
            True if registered, False otherwise.
        """
        return name in self._tools

    def __len__(self) -> int:
        """Get the number of registered tools.

        Returns:
            The number of tools.
        """
        return len(self._tools)


# Built-in coding tools


class ReadFileTool(Tool):
    """Tool for reading file contents.

    Example:
        >>> tool = ReadFileTool()
        >>> content = tool.execute(path="file.py")
    """

    def __init__(self):
        """Initialize the ReadFileTool."""
        super().__init__(
            name="read_file",
            description="Read the contents of a file",
            parameters=[
                ToolParameter(
                    name="path",
                    param_type=ParameterType.STRING,
                    description="The path to the file to read",
                    required=True,
                ),
                ToolParameter(
                    name="encoding",
                    param_type=ParameterType.STRING,
                    description="The file encoding (default: utf-8)",
                    required=False,
                    default="utf-8",
                ),
            ],
        )

    def execute(self, **kwargs: Any) -> str:
        """Read file contents.

        Args:
            path: The file path.
            encoding: The file encoding (default: utf-8).
            **kwargs: Additional arguments (ignored).

        Returns:
            The file contents.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        path = kwargs.get("path")
        if path is None:
            raise ValueError("Missing required parameter: path")
        encoding = kwargs.get("encoding", "utf-8")
        
        with open(path, "r", encoding=encoding) as f:
            return f.read()


class WriteFileTool(Tool):
    """Tool for writing file contents.

    Example:
        >>> tool = WriteFileTool()
        >>> tool.execute(path="file.py", content="print('hello')")
    """

    def __init__(self):
        """Initialize the WriteFileTool."""
        super().__init__(
            name="write_file",
            description="Write content to a file",
            parameters=[
                ToolParameter(
                    name="path",
                    param_type=ParameterType.STRING,
                    description="The path to the file to write",
                    required=True,
                ),
                ToolParameter(
                    name="content",
                    param_type=ParameterType.STRING,
                    description="The content to write",
                    required=True,
                ),
                ToolParameter(
                    name="encoding",
                    param_type=ParameterType.STRING,
                    description="The file encoding (default: utf-8)",
                    required=False,
                    default="utf-8",
                ),
            ],
        )

    def execute(self, **kwargs: Any) -> bool:
        """Write content to a file.

        Args:
            path: The file path.
            content: The content to write.
            encoding: The file encoding (default: utf-8).
            **kwargs: Additional arguments (ignored).

        Returns:
            True if successful.
        """
        path = kwargs.get("path")
        content = kwargs.get("content")
        if path is None:
            raise ValueError("Missing required parameter: path")
        if content is None:
            raise ValueError("Missing required parameter: content")
        encoding = kwargs.get("encoding", "utf-8")
        
        with open(path, "w", encoding=encoding) as f:
            f.write(content)
        return True


class ExecuteCodeTool(Tool):
    """Tool for executing Python code.

    WARNING: This tool executes arbitrary code. Use with caution.
    By default, only safe builtins are available.

    Example:
        >>> tool = ExecuteCodeTool()
        >>> result = tool.execute(code="result = 2 + 2")
    """

    # Safe builtins that don't allow dangerous operations
    SAFE_BUILTINS = {
        "abs": abs,
        "all": all,
        "any": any,
        "bool": bool,
        "dict": dict,
        "enumerate": enumerate,
        "filter": filter,
        "float": float,
        "int": int,
        "len": len,
        "list": list,
        "map": map,
        "max": max,
        "min": min,
        "print": print,
        "range": range,
        "round": round,
        "set": set,
        "sorted": sorted,
        "str": str,
        "sum": sum,
        "tuple": tuple,
        "type": type,
        "zip": zip,
        "True": True,
        "False": False,
        "None": None,
    }

    def __init__(self, allow_unsafe: bool = False):
        """Initialize the ExecuteCodeTool.

        Args:
            allow_unsafe: If True, allows access to all builtins.
                WARNING: Only set this to True in trusted environments.
        """
        super().__init__(
            name="execute_code",
            description="Execute Python code and return the result",
            parameters=[
                ToolParameter(
                    name="code",
                    param_type=ParameterType.STRING,
                    description="The Python code to execute",
                    required=True,
                ),
            ],
        )
        self.allow_unsafe = allow_unsafe

    def execute(self, **kwargs: Any) -> Any:
        """Execute Python code.

        Args:
            code: The Python code to execute.
            **kwargs: Additional arguments (ignored).

        Returns:
            The execution result (value of 'result' variable).

        Raises:
            Exception: If code execution fails.
            ValueError: If code contains potentially dangerous operations.

        Note:
            The dangerous pattern check is a basic safety measure and not a
            complete sandbox. It uses regex to detect common dangerous patterns
            but may not catch all possible exploits.
        """
        code = kwargs.get("code")
        if code is None:
            raise ValueError("Missing required parameter: code")
        
        # Check for potentially dangerous patterns when not in unsafe mode
        if not self.allow_unsafe:
            # Use regex patterns to catch variations (tabs, newlines, etc.)
            # Note: The '\bimport\b' pattern matches both regular import statements
            # (e.g., 'import os') and from-import statements (e.g., 'from os import path').
            # The pattern name "import statement" is used generically to cover both forms.
            dangerous_patterns = [
                (r'\bimport\b', "import statement"),
                (r'\b__import__\b', "__import__"),
                (r'\bexec\s*\(', "exec()"),
                (r'\beval\s*\(', "eval()"),
                (r'\bcompile\s*\(', "compile()"),
                (r'\bopen\s*\(', "open()"),
                (r'\bfile\s*\(', "file()"),
                (r'__builtins__', "__builtins__"),
                (r'__class__', "__class__"),
                (r'__bases__', "__bases__"),
                (r'__subclasses__', "__subclasses__"),
                (r'\bglobals\s*\(', "globals()"),
                (r'\blocals\s*\(', "locals()"),
                (r'\bgetattr\s*\(', "getattr()"),
                (r'\bsetattr\s*\(', "setattr()"),
                (r'\bdelattr\s*\(', "delattr()"),
            ]
            for pattern, name in dangerous_patterns:
                if regex_module.search(pattern, code):
                    raise ValueError(
                        f"Code contains potentially dangerous pattern: {name}"
                    )

        # Create execution environment
        if self.allow_unsafe:
            exec_globals = {"__builtins__": __builtins__}
        else:
            exec_globals = {"__builtins__": self.SAFE_BUILTINS}

        local_vars: Dict[str, Any] = {}
        exec(code, exec_globals, local_vars)
        return local_vars.get("result", None)


class SearchCodeTool(Tool):
    """Tool for searching code in files.

    Example:
        >>> tool = SearchCodeTool()
        >>> results = tool.execute(pattern="def main", directory="src/")
    """

    def __init__(self):
        """Initialize the SearchCodeTool."""
        super().__init__(
            name="search_code",
            description="Search for patterns in code files",
            parameters=[
                ToolParameter(
                    name="pattern",
                    param_type=ParameterType.STRING,
                    description="The pattern to search for",
                    required=True,
                ),
                ToolParameter(
                    name="directory",
                    param_type=ParameterType.STRING,
                    description="The directory to search in",
                    required=False,
                    default=".",
                ),
                ToolParameter(
                    name="extensions",
                    param_type=ParameterType.ARRAY,
                    description="File extensions to search (e.g., ['.py', '.js'])",
                    required=False,
                    default=[".py"],
                ),
            ],
        )

    def execute(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """Search for patterns in code files.

        Args:
            pattern: The pattern to search for.
            directory: The directory to search in (default: ".").
            extensions: File extensions to search (default: [".py"]).
            **kwargs: Additional arguments (ignored).

        Returns:
            List of matches with file, line number, and content.
        """
        pattern = kwargs.get("pattern")
        if pattern is None:
            raise ValueError("Missing required parameter: pattern")
        directory = kwargs.get("directory", ".")
        extensions = kwargs.get("extensions")
        
        import os
        import re

        if extensions is None:
            extensions = [".py"]

        results = []
        regex = re.compile(pattern)

        for root, _, files in os.walk(directory):
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            for i, line in enumerate(f, 1):
                                if regex.search(line):
                                    results.append(
                                        {
                                            "file": filepath,
                                            "line": i,
                                            "content": line.strip(),
                                        }
                                    )
                    except (IOError, UnicodeDecodeError):
                        continue

        return results


def create_default_registry() -> ToolRegistry:
    """Create a registry with default coding tools.

    Returns:
        A ToolRegistry with built-in coding tools.

    Example:
        >>> registry = create_default_registry()
        >>> content = registry.execute("read_file", path="main.py")
    """
    registry = ToolRegistry()
    registry.register(ReadFileTool())
    registry.register(WriteFileTool())
    registry.register(ExecuteCodeTool())
    registry.register(SearchCodeTool())
    return registry
