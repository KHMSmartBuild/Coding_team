# Core Module Documentation

The `core` module provides the foundational components for the Coding Team framework, including:

- **Dependency Injection**: A lightweight DI container for managing service dependencies
- **LLM Providers**: Abstract interfaces and implementations for various LLM providers
- **Tools**: A framework for defining and registering tools that can be used by LLM agents

## Table of Contents

1. [Dependency Injection Container](#dependency-injection-container)
2. [LLM Providers](#llm-providers)
3. [Tools Framework](#tools-framework)
4. [Integration Examples](#integration-examples)

---

## Dependency Injection Container

The `Container` class provides a centralized location for registering and resolving dependencies.

### Basic Usage

```python
from core.container import Container

# Create a container
container = Container()

# Register a singleton service
container.register("config", {"api_key": "xxx", "debug": True})

# Resolve the service
config = container.resolve("config")
print(config["api_key"])  # Output: xxx
```

### Service Lifetimes

The container supports three service lifetimes:

1. **Singleton**: Created once, shared across all requests
2. **Transient**: New instance created for each request
3. **Factory**: Custom factory function called each time

```python
from core.container import Container, ServiceLifetime

container = Container()

# Singleton (default)
container.register("database", DatabaseConnection())

# Transient - new instance each time
container.register_transient("handler", RequestHandler)

# Factory - custom creation logic
container.register_factory("logger", lambda c: get_logger(c.resolve("config")["name"]))
```

### Parent-Child Containers

Create scoped containers for hierarchical dependency resolution:

```python
# Application-level container
app_container = Container()
app_container.register("config", app_config)

# Request-level container
request_container = app_container.create_child()
request_container.register("request", current_request)

# Child can resolve from parent
config = request_container.resolve("config")  # From parent
request = request_container.resolve("request")  # From child
```

### Global Container

A global container is available for convenience:

```python
from core.container import get_global_container, reset_global_container

# Get or create global container
container = get_global_container()
container.register("service", my_service)

# Reset for testing
reset_global_container()
```

---

## LLM Providers

The `llm_provider` module provides abstract interfaces and implementations for various LLM providers.

### Configuration

```python
from core.llm_provider import LLMConfig

# Basic configuration
config = LLMConfig(
    api_key="sk-xxx",
    model="gpt-4",
    temperature=0.7,
    max_tokens=4096
)

# Configuration from environment variables
# If api_key is None, it looks for OPENAI_API_KEY or LLM_API_KEY
config = LLMConfig(model="gpt-4")
```

### Supported Providers

#### OpenAI Provider

```python
from core.llm_provider import OpenAIProvider, LLMConfig

config = LLMConfig(api_key="sk-xxx", model="gpt-4")
provider = OpenAIProvider(config)

# Generate text
response = provider.generate("Explain quantum computing")
print(response.content)
print(f"Tokens used: {response.total_tokens}")
```

#### Anthropic Provider

```python
from core.llm_provider import AnthropicProvider, LLMConfig

config = LLMConfig(model="claude-3-sonnet-20240229")
provider = AnthropicProvider(config)

response = provider.generate("Explain machine learning")
print(response.content)
```

#### Mock Provider (for testing)

```python
from core.llm_provider import MockLLMProvider

provider = MockLLMProvider()

# Set custom responses
provider.set_response("Custom response text")
response = provider.generate("Any prompt")
print(response.content)  # Output: Custom response text

# Check call history
print(provider.call_history)
```

### Factory Function

Use the factory function to create providers dynamically:

```python
from core.llm_provider import create_provider, LLMConfig

# Create by name
provider = create_provider("openai", LLMConfig(api_key="xxx"))

# Supported: "openai", "anthropic", "mock"
mock = create_provider("mock")
```

### Chat Conversations

```python
from core.llm_provider import OpenAIProvider, Message

provider = OpenAIProvider(config)

messages = [
    Message(role="system", content="You are a helpful assistant."),
    Message(role="user", content="Hello!"),
]

response = provider.generate_chat(messages)
print(response.content)
```

### Response Object

```python
from core.llm_provider import LLMResponse

# Response attributes
response.content          # Generated text
response.model            # Model used
response.prompt_tokens    # Input tokens
response.completion_tokens # Output tokens
response.total_tokens     # Total tokens
response.finish_reason    # Stop reason
response.success          # True if content exists
```

---

## Tools Framework

The `tools` module provides a framework for defining and registering tools for LLM agents.

### Defining Tools

#### Using Classes

```python
from core.tools import Tool, ToolParameter, ToolResult

class SearchTool(Tool):
    name = "search"
    description = "Search the web for information"
    parameters = [
        ToolParameter(
            name="query",
            type="string",
            description="Search query",
            required=True
        ),
        ToolParameter(
            name="limit",
            type="integer",
            description="Max results",
            required=False,
            default=10
        )
    ]

    def execute(self, **kwargs) -> ToolResult:
        query = kwargs.get("query")
        # Implementation here
        return ToolResult(
            success=True,
            output=f"Results for: {query}"
        )

# Use the tool
tool = SearchTool()
result = tool(query="python tutorials")
print(result.output)
```

#### Using Decorators

```python
from core.tools import Tool, ToolParameter

@Tool.define(
    name="calculator",
    description="Perform math calculations",
    parameters=[
        ToolParameter(name="expression", type="string", description="Math expression")
    ]
)
def calculate(expression: str) -> str:
    return str(eval(expression))

result = calculate(expression="2 + 2")
print(result.output)  # Output: 4
```

#### Using Functions Directly

```python
from core.tools import FunctionTool

def greet(name: str) -> str:
    """Say hello to someone."""
    return f"Hello, {name}!"

tool = FunctionTool(greet)
result = tool(name="World")
print(result.output)  # Output: Hello, World!
```

### Tool Registry

```python
from core.tools import ToolRegistry

# Create registry
registry = ToolRegistry()

# Register tools
registry.register(SearchTool(), category="search")
registry.register(calculate, category="math")

# List tools
print(registry.list_tools())
print(registry.list_categories())

# Execute by name
result = registry.execute("search", query="python")

# Get schemas for OpenAI
schemas = registry.to_openai_format()
```

### Built-in Tools

```python
from core.tools import get_default_tools

# Get default tools registry
registry = get_default_tools()

# Available tools:
# - code_analysis: Analyze code quality
# - file_operation: Read/write files
# - test_runner: Run tests

# Code analysis
result = registry.execute("code_analysis", 
    code="def foo(): pass",
    language="python",
    checks=["style"]
)

# File operations
result = registry.execute("file_operation",
    operation="read",
    path="./file.txt"
)
```

### OpenAI Function Calling Integration

```python
from core.tools import ToolRegistry, FunctionTool

# Define tools
def search_web(query: str) -> str:
    return f"Results for {query}"

def get_weather(city: str) -> str:
    return f"Weather in {city}: Sunny"

# Register
registry = ToolRegistry()
registry.register(search_web, category="search")
registry.register(get_weather, category="weather")

# Get OpenAI-compatible tool definitions
tools = registry.to_openai_format()

# Use with OpenAI API
# response = openai.chat.completions.create(
#     model="gpt-4",
#     messages=[...],
#     tools=tools
# )
```

---

## Integration Examples

### Complete Agent Setup

```python
from core.container import Container
from core.llm_provider import OpenAIProvider, LLMConfig
from core.tools import ToolRegistry, get_default_tools

# Create container
container = Container()

# Configure LLM
config = LLMConfig(
    api_key="sk-xxx",
    model="gpt-4",
    temperature=0.7
)
provider = OpenAIProvider(config)

# Register in container
container.register("llm_provider", provider)
container.register("tools", get_default_tools())

# Use in agent
from Agents.A1_Project_Manager.Agent_Project_Manager import ProjectManager

manager = ProjectManager(
    llm_provider=container.resolve("llm_provider"),
    project_name="My Project"
)

tasks = {
    "Agent_1": {"task": "Code review", "priority": 1}
}
result = manager.run(tasks)
```

### Testing with Mock Provider

```python
import pytest
from core.llm_provider import MockLLMProvider
from core.container import Container

@pytest.fixture
def test_container():
    container = Container()
    
    mock_llm = MockLLMProvider()
    mock_llm.set_responses(["Test response 1", "Test response 2"])
    
    container.register("llm_provider", mock_llm)
    return container

def test_agent_behavior(test_container):
    provider = test_container.resolve("llm_provider")
    response = provider.generate("Test prompt")
    
    assert response.content == "Test response 1"
    assert len(provider.call_history) == 1
```

---

## API Reference

### Container

| Method | Description |
|--------|-------------|
| `register(name, service, lifetime)` | Register a service |
| `register_singleton(name, service)` | Register singleton |
| `register_transient(name, service)` | Register transient |
| `register_factory(name, factory)` | Register factory |
| `resolve(name)` | Get a service |
| `has(name)` | Check if registered |
| `unregister(name)` | Remove a service |
| `clear()` | Remove all services |
| `create_child()` | Create child container |

### LLMProvider

| Method | Description |
|--------|-------------|
| `generate(prompt)` | Generate text from prompt |
| `generate_chat(messages)` | Generate chat response |
| `validate_config()` | Validate configuration |
| `initialize()` | Initialize provider |

### ToolRegistry

| Method | Description |
|--------|-------------|
| `register(tool, category)` | Register a tool |
| `unregister(name)` | Remove a tool |
| `get(name)` | Get tool by name |
| `execute(name, **kwargs)` | Execute a tool |
| `list_tools(category)` | List tool names |
| `get_all_schemas()` | Get all tool schemas |
| `to_openai_format()` | Get OpenAI-compatible schemas |

---

## Best Practices

1. **Use dependency injection**: Register services in container for testability
2. **Use mock provider in tests**: Avoid real API calls in tests
3. **Define tools explicitly**: Use clear names and descriptions
4. **Handle errors gracefully**: Check `ToolResult.success` before using output
5. **Use appropriate service lifetimes**: Singleton for shared state, transient for request-specific
