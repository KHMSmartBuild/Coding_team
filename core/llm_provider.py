"""
LLM Provider Abstraction Module.

This module provides an abstract interface for Language Model providers with
implementations for OpenAI, Anthropic, and a Mock provider for testing.

Example:
    >>> provider = OpenAIProvider(api_key="your-api-key")
    >>> response = provider.generate("What is Python?")
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union


class ModelProvider(Enum):
    """Enumeration of supported model providers.

    Attributes:
        OPENAI: OpenAI GPT models.
        ANTHROPIC: Anthropic Claude models.
        MOCK: Mock provider for testing.
    """

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    MOCK = "mock"


@dataclass
class Message:
    """Represents a message in a conversation.

    Attributes:
        role: The role of the message sender (system, user, assistant).
        content: The content of the message.
    """

    role: str
    content: str


@dataclass
class LLMResponse:
    """Response from an LLM provider.

    Attributes:
        content: The generated text content.
        model: The model used for generation.
        usage: Token usage statistics.
        raw_response: The raw response from the provider.
        finish_reason: The reason generation stopped.
    """

    content: str
    model: str = ""
    usage: Dict[str, int] = field(default_factory=dict)
    raw_response: Optional[Any] = None
    finish_reason: str = ""


@dataclass
class LLMConfig:
    """Configuration for LLM providers.

    Attributes:
        model: The model identifier.
        temperature: Sampling temperature (0.0 to 2.0).
        max_tokens: Maximum tokens to generate.
        top_p: Nucleus sampling parameter.
        frequency_penalty: Frequency penalty for token repetition.
        presence_penalty: Presence penalty for topic repetition.
        stop: Stop sequences.
        timeout: Request timeout in seconds.
    """

    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 1000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop: Optional[List[str]] = None
    timeout: int = 30


class LLMProviderError(Exception):
    """Exception raised for LLM provider errors.

    Attributes:
        message: Explanation of the error.
        provider: The provider that raised the error.
    """

    def __init__(self, message: str, provider: str = "unknown"):
        """Initialize the error.

        Args:
            message: The error message.
            provider: The provider that raised the error.
        """
        self.message = message
        self.provider = provider
        super().__init__(f"[{provider}] {message}")


class LLMProvider(ABC):
    """Abstract base class for LLM providers.

    This class defines the interface that all LLM providers must implement.

    Attributes:
        config: The LLM configuration.

    Example:
        >>> class MyProvider(LLMProvider):
        ...     def generate(self, prompt, **kwargs):
        ...         return LLMResponse(content="Hello!")
    """

    def __init__(self, config: Optional[LLMConfig] = None):
        """Initialize the provider.

        Args:
            config: Optional LLM configuration.
        """
        self.config = config or LLMConfig()

    @abstractmethod
    def generate(
        self,
        prompt: str,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate text from a prompt.

        Args:
            prompt: The input prompt.
            **kwargs: Additional provider-specific arguments.

        Returns:
            An LLMResponse containing the generated text.

        Raises:
            LLMProviderError: If generation fails.
        """
        pass

    @abstractmethod
    def chat(
        self,
        messages: List[Message],
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate a chat response from messages.

        Args:
            messages: List of conversation messages.
            **kwargs: Additional provider-specific arguments.

        Returns:
            An LLMResponse containing the generated response.

        Raises:
            LLMProviderError: If generation fails.
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get the provider name.

        Returns:
            The name of the provider.
        """
        pass

    def update_config(self, **kwargs: Any) -> None:
        """Update configuration parameters.

        Args:
            **kwargs: Configuration parameters to update.

        Example:
            >>> provider.update_config(temperature=0.5, max_tokens=500)
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)


class OpenAIProvider(LLMProvider):
    """OpenAI LLM Provider.

    Provides integration with OpenAI's GPT models.

    Attributes:
        api_key: The OpenAI API key.
        organization: Optional organization ID.
        client: The OpenAI client instance.

    Example:
        >>> provider = OpenAIProvider(api_key="sk-...")
        >>> response = provider.generate("Hello, world!")
    """

    def __init__(
        self,
        api_key: str,
        organization: Optional[str] = None,
        config: Optional[LLMConfig] = None,
    ):
        """Initialize the OpenAI provider.

        Args:
            api_key: The OpenAI API key.
            organization: Optional organization ID.
            config: Optional LLM configuration.
        """
        super().__init__(config)
        self.api_key = api_key
        self.organization = organization
        self._client: Optional[Any] = None

    @property
    def client(self) -> Any:
        """Get or create the OpenAI client.

        Returns:
            The OpenAI client instance.

        Raises:
            LLMProviderError: If the openai package is not installed.
        """
        if self._client is None:
            try:
                from openai import OpenAI

                self._client = OpenAI(
                    api_key=self.api_key,
                    organization=self.organization,
                )
            except ImportError:
                raise LLMProviderError(
                    "The 'openai' package is required. Install it with: pip install openai",
                    provider=self.provider_name,
                )
        return self._client

    @property
    def provider_name(self) -> str:
        """Get the provider name.

        Returns:
            The provider name 'openai'.
        """
        return "openai"

    def generate(
        self,
        prompt: str,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate text from a prompt using OpenAI.

        Args:
            prompt: The input prompt.
            **kwargs: Additional arguments (temperature, max_tokens, etc.).

        Returns:
            An LLMResponse containing the generated text.

        Raises:
            LLMProviderError: If generation fails.
        """
        messages = [Message(role="user", content=prompt)]
        return self.chat(messages, **kwargs)

    def chat(
        self,
        messages: List[Message],
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate a chat response using OpenAI.

        Args:
            messages: List of conversation messages.
            **kwargs: Additional arguments.

        Returns:
            An LLMResponse containing the generated response.

        Raises:
            LLMProviderError: If generation fails.
        """
        try:
            formatted_messages = [
                {"role": msg.role, "content": msg.content} for msg in messages
            ]

            response = self.client.chat.completions.create(
                model=kwargs.get("model", self.config.model),
                messages=formatted_messages,
                temperature=kwargs.get("temperature", self.config.temperature),
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                top_p=kwargs.get("top_p", self.config.top_p),
                frequency_penalty=kwargs.get(
                    "frequency_penalty", self.config.frequency_penalty
                ),
                presence_penalty=kwargs.get(
                    "presence_penalty", self.config.presence_penalty
                ),
                stop=kwargs.get("stop", self.config.stop),
            )

            choice = response.choices[0]
            return LLMResponse(
                content=choice.message.content or "",
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }
                if response.usage
                else {},
                raw_response=response,
                finish_reason=choice.finish_reason or "",
            )
        except Exception as e:
            raise LLMProviderError(str(e), provider=self.provider_name)


class AnthropicProvider(LLMProvider):
    """Anthropic LLM Provider.

    Provides integration with Anthropic's Claude models.

    Attributes:
        api_key: The Anthropic API key.
        client: The Anthropic client instance.

    Example:
        >>> provider = AnthropicProvider(api_key="sk-ant-...")
        >>> response = provider.generate("Hello, Claude!")
    """

    def __init__(
        self,
        api_key: str,
        config: Optional[LLMConfig] = None,
    ):
        """Initialize the Anthropic provider.

        Args:
            api_key: The Anthropic API key.
            config: Optional LLM configuration.
        """
        super().__init__(config)
        if config is None:
            self.config.model = "claude-3-sonnet-20240229"
        self.api_key = api_key
        self._client: Optional[Any] = None

    @property
    def client(self) -> Any:
        """Get or create the Anthropic client.

        Returns:
            The Anthropic client instance.

        Raises:
            LLMProviderError: If the anthropic package is not installed.
        """
        if self._client is None:
            try:
                from anthropic import Anthropic

                self._client = Anthropic(api_key=self.api_key)
            except ImportError:
                raise LLMProviderError(
                    "The 'anthropic' package is required. Install it with: pip install anthropic",
                    provider=self.provider_name,
                )
        return self._client

    @property
    def provider_name(self) -> str:
        """Get the provider name.

        Returns:
            The provider name 'anthropic'.
        """
        return "anthropic"

    def generate(
        self,
        prompt: str,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate text from a prompt using Anthropic.

        Args:
            prompt: The input prompt.
            **kwargs: Additional arguments.

        Returns:
            An LLMResponse containing the generated text.

        Raises:
            LLMProviderError: If generation fails.
        """
        messages = [Message(role="user", content=prompt)]
        return self.chat(messages, **kwargs)

    def chat(
        self,
        messages: List[Message],
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate a chat response using Anthropic.

        Args:
            messages: List of conversation messages.
            **kwargs: Additional arguments.

        Returns:
            An LLMResponse containing the generated response.

        Raises:
            LLMProviderError: If generation fails.
        """
        try:
            # Extract system message if present
            system_message = None
            chat_messages = []
            for msg in messages:
                if msg.role == "system":
                    system_message = msg.content
                else:
                    chat_messages.append({"role": msg.role, "content": msg.content})

            create_kwargs = {
                "model": kwargs.get("model", self.config.model),
                "messages": chat_messages,
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", self.config.temperature),
                "top_p": kwargs.get("top_p", self.config.top_p),
            }

            if system_message:
                create_kwargs["system"] = system_message

            if kwargs.get("stop", self.config.stop):
                create_kwargs["stop_sequences"] = kwargs.get("stop", self.config.stop)

            response = self.client.messages.create(**create_kwargs)

            return LLMResponse(
                content=response.content[0].text if response.content else "",
                model=response.model,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                }
                if response.usage
                else {},
                raw_response=response,
                finish_reason=response.stop_reason or "",
            )
        except Exception as e:
            raise LLMProviderError(str(e), provider=self.provider_name)


class MockProvider(LLMProvider):
    """Mock LLM Provider for testing.

    Provides a mock implementation for testing without API calls.

    Attributes:
        responses: List of predefined responses.
        response_index: Current index in the responses list.
        calls: List of recorded calls.

    Example:
        >>> provider = MockProvider(responses=["Hello!", "How can I help?"])
        >>> response = provider.generate("Hi")
        >>> print(response.content)  # "Hello!"
    """

    def __init__(
        self,
        responses: Optional[List[str]] = None,
        config: Optional[LLMConfig] = None,
    ):
        """Initialize the Mock provider.

        Args:
            responses: List of predefined responses to return.
            config: Optional LLM configuration.
        """
        super().__init__(config)
        self.responses = responses or ["Mock response"]
        self.response_index = 0
        self.calls: List[Dict[str, Any]] = []

    @property
    def provider_name(self) -> str:
        """Get the provider name.

        Returns:
            The provider name 'mock'.
        """
        return "mock"

    def generate(
        self,
        prompt: str,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate a mock response.

        Args:
            prompt: The input prompt.
            **kwargs: Additional arguments (ignored).

        Returns:
            An LLMResponse with the next predefined response.
        """
        self.calls.append({"method": "generate", "prompt": prompt, "kwargs": kwargs})
        return self._get_response()

    def chat(
        self,
        messages: List[Message],
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate a mock chat response.

        Args:
            messages: List of conversation messages.
            **kwargs: Additional arguments (ignored).

        Returns:
            An LLMResponse with the next predefined response.
        """
        self.calls.append({"method": "chat", "messages": messages, "kwargs": kwargs})
        return self._get_response()

    def _get_response(self) -> LLMResponse:
        """Get the next response from the list.

        Returns:
            An LLMResponse with the next predefined response.
        """
        content = self.responses[self.response_index % len(self.responses)]
        self.response_index += 1

        return LLMResponse(
            content=content,
            model="mock-model",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            finish_reason="stop",
        )

    def reset(self) -> None:
        """Reset the provider state.

        Clears the calls list and resets the response index.
        """
        self.response_index = 0
        self.calls.clear()

    def add_response(self, response: str) -> None:
        """Add a response to the list.

        Args:
            response: The response to add.
        """
        self.responses.append(response)


def create_provider(
    provider_type: Union[str, ModelProvider],
    api_key: Optional[str] = None,
    config: Optional[LLMConfig] = None,
    **kwargs: Any,
) -> LLMProvider:
    """Factory function to create LLM providers.

    Args:
        provider_type: The type of provider to create.
        api_key: The API key for the provider.
        config: Optional LLM configuration.
        **kwargs: Additional provider-specific arguments.

    Returns:
        An LLM provider instance.

    Raises:
        ValueError: If the provider type is not supported.

    Example:
        >>> provider = create_provider("openai", api_key="sk-...")
    """
    if isinstance(provider_type, str):
        provider_type = ModelProvider(provider_type.lower())

    if provider_type == ModelProvider.OPENAI:
        if api_key is None:
            raise ValueError("API key is required for OpenAI provider")
        return OpenAIProvider(
            api_key=api_key,
            organization=kwargs.get("organization"),
            config=config,
        )
    elif provider_type == ModelProvider.ANTHROPIC:
        if api_key is None:
            raise ValueError("API key is required for Anthropic provider")
        return AnthropicProvider(api_key=api_key, config=config)
    elif provider_type == ModelProvider.MOCK:
        return MockProvider(responses=kwargs.get("responses"), config=config)
    else:
        raise ValueError(f"Unsupported provider type: {provider_type}")
