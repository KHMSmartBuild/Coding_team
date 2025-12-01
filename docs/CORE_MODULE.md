# Core Module Documentation

The Core module provides foundational infrastructure for the Coding Team project, including dependency injection, LLM provider abstractions, and a tools framework for agent integration.

## Table of Contents

- [Installation](#installation)
- [Dependency Injection Container](#dependency-injection-container)
- [LLM Provider Abstractions](#llm-provider-abstractions)
- [Tools Framework](#tools-framework)
- [API Reference](#api-reference)

## Installation

The core module is included in the Coding Team package. No additional installation is required.

```python
from core import Container, create_provider, ToolRegistry
```

## Dependency Injection Container

The Container class provides a lightweight dependency injection system with support for multiple service lifetimes.

### Service Lifetimes

- **Singleton**: A single instance is created and reused for all requests
- **Transient**: A new instance is created for each request
- **Factory**: A factory function is called for each request

### Basic Usage

```python
from core import Container

# Create a container
container = Container()

# Register a singleton service
container.register_singleton("config", {"debug": True, "timeout": 30})

# Register a transient service
class RequestHandler:
    def handle(self):
        pass

container.register_transient("request_handler", RequestHandler)

# Register a factory service
container.register_factory("connection", lambda: DatabaseConnection())

# Resolve services
config = container.resolve("config")
handler = container.resolve("request_handler")  # New instance each time
connection = container.resolve("connection")  # Factory called each time
```

### Hierarchical Containers

Child containers can inherit and override parent services:

```python
# Create parent container
parent = Container()
parent.register_singleton("logger", ConsoleLogger())

# Create child container
child = parent.create_child()
child.register_singleton("logger", FileLogger())  # Override parent

# Child resolves its own logger, but can still access parent services
logger = child.resolve("logger")  # FileLogger
```

### Method Chaining

Container methods support fluent chaining:

```python
container = Container()
container.register_singleton("config", config) \
         .register_transient("handler", Handler) \
         .register_factory("connection", create_connection)
```

## LLM Provider Abstractions

The LLM provider system provides a unified interface for working with different language model providers.

### Supported Providers

- **OpenAI**: GPT models (GPT-3.5, GPT-4, etc.)
- **Anthropic**: Claude models (Claude 3 Sonnet, etc.)
- **Mock**: For testing without API calls

### Creating Providers

```python
from core import create_provider, LLMConfig

# Create an OpenAI provider
openai_provider = create_provider(
    "openai",
    api_key="sk-your-api-key",
    config=LLMConfig(model="gpt-4", temperature=0.7)
)

# Create an Anthropic provider
anthropic_provider = create_provider(
    "anthropic",
    api_key="sk-ant-your-api-key",
    config=LLMConfig(model="claude-3-sonnet-20240229")
)

# Create a mock provider for testing
mock_provider = create_provider(
    "mock",
    responses=["Response 1", "Response 2"]
)
```

### Using Providers

```python
from core import Message

# Simple text generation
response = provider.generate("What is Python?")
print(response.content)

# Chat-style conversation
messages = [
    Message(role="system", content="You are a helpful assistant."),
    Message(role="user", content="What is dependency injection?")
]
response = provider.chat(messages)
print(response.content)

# Access response metadata
print(f"Model: {response.model}")
print(f"Tokens used: {response.usage}")
```

### Configuration Options

```python
from core import LLMConfig

config = LLMConfig(
    model="gpt-4",              # Model identifier
    temperature=0.7,            # Sampling temperature (0.0-2.0)
    max_tokens=1000,            # Maximum tokens to generate
    top_p=1.0,                  # Nucleus sampling parameter
    frequency_penalty=0.0,      # Frequency penalty
    presence_penalty=0.0,       # Presence penalty
    stop=["END"],               # Stop sequences
    timeout=30                  # Request timeout in seconds
)
```

## Tools Framework

The tools framework allows creating tools that can be used by AI agents for function calling.

### Creating Tools

#### Using the Decorator

```python
from core import tool

@tool(name="calculator", description="Perform arithmetic operations")
def calculator(operation: str, a: float, b: float) -> float:
    """Calculate the result of an arithmetic operation."""
    ops = {
        "add": lambda: a + b,
        "subtract": lambda: a - b,
        "multiply": lambda: a * b,
        "divide": lambda: a / b,
    }
    return ops[operation]()
```

#### Using FunctionTool

```python
from core import FunctionTool

def greet(name: str) -> str:
    """Greet a person by name."""
    return f"Hello, {name}!"

greet_tool = FunctionTool(
    greet,
    name="greet",
    description="Greet a person by name"
)
```

#### Creating Custom Tool Classes

```python
from core import Tool, ToolParameter, ParameterType

class DatabaseQueryTool(Tool):
    def __init__(self, connection_string: str):
        super().__init__(
            name="query_database",
            description="Execute a SQL query",
            parameters=[
                ToolParameter(
                    name="query",
                    param_type=ParameterType.STRING,
                    description="The SQL query to execute",
                    required=True
                )
            ]
        )
        self.connection_string = connection_string

    def execute(self, query: str, **kwargs) -> list:
        # Execute query and return results
        pass
```

### Tool Registry

```python
from core import ToolRegistry, create_default_registry

# Create a registry with default coding tools
registry = create_default_registry()

# Or create an empty registry
registry = ToolRegistry()

# Register tools
registry.register(calculator)
registry.register(greet_tool)

# Execute tools
result = registry.execute("calculator", operation="add", a=5, b=3)
print(result)  # 8

# List registered tools
print(registry.list_tools())  # ['calculator', 'greet', ...]
```

### OpenAI Function Calling

Generate schemas compatible with OpenAI's function calling:

```python
# Get OpenAI-compatible tool definitions
tools = registry.to_openai_tools()

# Use with OpenAI API
response = client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)
```

### Built-in Tools

The framework includes several built-in coding tools:

- **ReadFileTool**: Read file contents
- **WriteFileTool**: Write content to files
- **ExecuteCodeTool**: Execute Python code (use with caution)
- **SearchCodeTool**: Search for patterns in code files

```python
from core import create_default_registry

registry = create_default_registry()

# Read a file
content = registry.execute("read_file", path="main.py")

# Write a file
registry.execute("write_file", path="output.txt", content="Hello!")

# Search code
results = registry.execute(
    "search_code",
    pattern="def main",
    directory="src/",
    extensions=[".py"]
)
```

## API Reference

### Container

| Method | Description |
|--------|-------------|
| `register_singleton(name, instance)` | Register a singleton service |
| `register_transient(name, service_type)` | Register a transient service |
| `register_factory(name, factory)` | Register a factory service |
| `resolve(name, **kwargs)` | Resolve a service by name |
| `is_registered(name)` | Check if a service is registered |
| `unregister(name)` | Unregister a service |
| `create_child()` | Create a child container |
| `clear()` | Clear all registered services |

### LLMProvider

| Method | Description |
|--------|-------------|
| `generate(prompt, **kwargs)` | Generate text from a prompt |
| `chat(messages, **kwargs)` | Generate a chat response |
| `update_config(**kwargs)` | Update configuration parameters |

### ToolRegistry

| Method | Description |
|--------|-------------|
| `register(tool, **kwargs)` | Register a tool |
| `unregister(name)` | Unregister a tool |
| `get(name)` | Get a tool by name |
| `execute(name, **kwargs)` | Execute a tool by name |
| `list_tools()` | List all registered tool names |
| `get_schemas()` | Get schemas for all tools |
| `to_openai_functions()` | Generate OpenAI function definitions |
| `to_openai_tools()` | Alias for to_openai_functions |
| `clear()` | Clear all registered tools |

## Examples

### Complete Example: AI Agent with DI

```python
from core import Container, create_provider, ToolRegistry, create_default_registry

# Set up container
container = Container()

# Register LLM provider
provider = create_provider("openai", api_key="sk-...")
container.register_singleton("llm_provider", provider)

# Register tools
tools = create_default_registry()
container.register_singleton("tools", tools)

# Use in agent
class CodingAgent:
    def __init__(self, container: Container):
        self.provider = container.resolve("llm_provider")
        self.tools = container.resolve("tools")

    def process(self, task: str) -> str:
        response = self.provider.generate(
            f"Complete this coding task: {task}"
        )
        return response.content

# Create and use agent
agent = CodingAgent(container)
result = agent.process("Write a hello world function")
```

### Testing with Mock Provider

```python
from core import Container, create_provider

def test_agent_behavior():
    # Set up mock provider
    mock = create_provider("mock", responses=[
        "def hello(): print('Hello!')",
        "Test passed"
    ])

    container = Container()
    container.register_singleton("llm_provider", mock)

    # Test agent behavior
    agent = CodingAgent(container)
    result = agent.process("Write a function")

    assert "def hello" in result
    assert len(mock.calls) == 1
```
