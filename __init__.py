"""
Coding Team - AI-Powered Software Development Framework.

This package provides the foundational components for the AI-powered coding team,
featuring 10 specialized AI agents for comprehensive software development tasks.

The package includes:
    - Core: Dependency injection, LLM providers, and tool definitions
    - Agents: 10 specialized AI agents for different development tasks
    - Helpers: Utility functions for common operations
    - Docs: Documentation and project tracking

Example:
    >>> from coding_team.core import Container, LLMConfig
    >>> from coding_team.helpers import DtO, StrO

Note:
    Agent modules have optional dependencies (langchain, openai, etc.).
    Core and helper modules work without these dependencies.

TODO(docs): Add comprehensive API documentation
TODO(feature): Add CLI interface for common operations
"""

__version__ = "0.2.0"
__author__ = "KHMSmartBuild"

# Core module imports (no external dependencies required)
# NOTE: These are always available
try:
    from core.container import Container, ServiceLifetime, get_global_container
    from core.llm_provider import LLMConfig, LLMProvider, LLMResponse, create_provider
    from core.tools import Tool, ToolRegistry, ToolResult, get_default_tools
except ImportError:
    # Graceful fallback if core module not fully initialized
    Container = None
    LLMConfig = None
    Tool = None

# Helper imports (minimal dependencies)
# NOTE: Always available
try:
    from helpers import DtO, FaDO, StrO, logging_config
except ImportError:
    DtO = None
    FaDO = None
    StrO = None

# Lazy imports for Agent modules to avoid requiring langchain
# NOTE: These modules have optional external dependencies
# Use: from Agents.A1_Project_Manager import Agent_Project_Manager


def get_agent_module(agent_name: str):
    """Dynamically import an agent module.

    This function provides lazy loading of agent modules to avoid
    requiring external dependencies (like langchain) at import time.

    Args:
        agent_name: Name of the agent module (e.g., 'A1_Project_Manager').

    Returns:
        The imported agent module or None if import fails.

    Example:
        >>> pm = get_agent_module('A1_Project_Manager')
        >>> if pm:
        ...     pm.project_manager(tasks)
    """
    import importlib
    try:
        return importlib.import_module(f"Agents.{agent_name}")
    except ImportError as e:
        import logging
        logging.warning(f"Could not import agent '{agent_name}': {e}")
        return None


__all__ = [
    # Version info
    "__version__",
    "__author__",
    # Core components
    "Container",
    "ServiceLifetime",
    "get_global_container",
    "LLMConfig",
    "LLMProvider",
    "LLMResponse",
    "create_provider",
    "Tool",
    "ToolRegistry",
    "ToolResult",
    "get_default_tools",
    # Helpers
    "DtO",
    "FaDO",
    "StrO",
    "logging_config",
    # Utilities
    "get_agent_module",
]
