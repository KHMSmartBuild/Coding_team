"""
Core module for the Coding Team framework.

This module provides the foundational components for the AI-powered coding team,
including dependency injection, LLM abstractions, and tool definitions.

Example:
    >>> from core.llm_provider import LLMProvider, OpenAIProvider
    >>> from core.container import Container
    >>> container = Container()
    >>> container.register('llm', OpenAIProvider())
"""

from core.container import Container
from core.llm_provider import (
    LLMProvider,
    LLMConfig,
    LLMResponse,
)
from core.tools import (
    Tool,
    ToolRegistry,
    ToolResult,
)

__all__ = [
    "Container",
    "LLMProvider",
    "LLMConfig",
    "LLMResponse",
    "Tool",
    "ToolRegistry",
    "ToolResult",
]
