"""
Core Module for Coding Team.

This module provides foundational infrastructure including:
- Dependency Injection Container
- LLM Provider Abstractions
- Tools Framework for Agent Integration

Example:
    >>> from core import Container, create_provider, ToolRegistry
    >>> container = Container()
    >>> provider = create_provider("mock")
    >>> registry = ToolRegistry()
"""

from core.container import (
    Container,
    ContainerError,
    ServiceDescriptor,
    ServiceLifetime,
)
from core.llm_provider import (
    AnthropicProvider,
    LLMConfig,
    LLMProvider,
    LLMProviderError,
    LLMResponse,
    Message,
    MockProvider,
    ModelProvider,
    OpenAIProvider,
    create_provider,
)
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

__all__ = [
    # Container
    "Container",
    "ContainerError",
    "ServiceDescriptor",
    "ServiceLifetime",
    # LLM Provider
    "LLMProvider",
    "LLMConfig",
    "LLMResponse",
    "LLMProviderError",
    "Message",
    "ModelProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "MockProvider",
    "create_provider",
    # Tools
    "Tool",
    "ToolParameter",
    "ToolSchema",
    "ToolRegistry",
    "FunctionTool",
    "ParameterType",
    "tool",
    "ReadFileTool",
    "WriteFileTool",
    "ExecuteCodeTool",
    "SearchCodeTool",
    "create_default_registry",
]
