"""
LLM Provider abstractions for the Coding Team framework.

This module provides abstract base classes and implementations for LLM providers,
following modern langchain-core design patterns. It enables dependency injection
of LLM components and supports multiple providers (OpenAI, Anthropic, etc.).

Example:
    >>> from core.llm_provider import OpenAIProvider, LLMConfig
    >>> config = LLMConfig(api_key='xxx', model='gpt-4')
    >>> provider = OpenAIProvider(config)
    >>> response = await provider.generate("Hello, world!")

Attributes:
    LLMConfig: Configuration dataclass for LLM providers.
    LLMResponse: Response dataclass from LLM providers.
    LLMProvider: Abstract base class for LLM providers.
    OpenAIProvider: OpenAI implementation of LLMProvider.
    AnthropicProvider: Anthropic implementation of LLMProvider.
    MockLLMProvider: Mock implementation for testing.

TODO(feature): Add support for streaming responses
TODO(feature): Add support for function calling
TODO(enhancement): Add rate limiting and retry logic
"""

import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

# Use standard logging with fallback
try:
    from helpers.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """Configuration for LLM providers.

    This dataclass holds all configuration options for LLM providers,
    including API keys, model selection, and generation parameters.

    Attributes:
        api_key: The API key for the LLM provider.
        model: The model name to use (e.g., 'gpt-4', 'claude-3-opus').
        temperature: Sampling temperature (0.0 to 2.0).
        max_tokens: Maximum number of tokens to generate.
        top_p: Nucleus sampling probability.
        frequency_penalty: Penalty for token frequency.
        presence_penalty: Penalty for token presence.
        timeout: Request timeout in seconds.
        base_url: Optional base URL for API requests.
        extra_params: Additional provider-specific parameters.

    Example:
        >>> config = LLMConfig(
        ...     api_key='sk-xxx',
        ...     model='gpt-4-turbo',
        ...     temperature=0.7,
        ...     max_tokens=4096
        ... )
    """
    api_key: Optional[str] = None
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: int = 60
    base_url: Optional[str] = None
    extra_params: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        # Try to get API key from environment if not provided
        if self.api_key is None:
            self.api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("LLM_API_KEY")

        # Validate temperature
        if not 0.0 <= self.temperature <= 2.0:
            logger.warning(f"Temperature {self.temperature} out of range, clamping to [0.0, 2.0]")
            self.temperature = max(0.0, min(2.0, self.temperature))


@dataclass
class LLMResponse:
    """Response from an LLM provider.

    This dataclass encapsulates the response from an LLM generation request,
    including the generated text, token usage, and metadata.

    Attributes:
        content: The generated text content.
        model: The model that generated the response.
        prompt_tokens: Number of tokens in the prompt.
        completion_tokens: Number of tokens in the completion.
        total_tokens: Total tokens used (prompt + completion).
        finish_reason: Reason for stopping generation.
        metadata: Additional response metadata.

    Example:
        >>> response = provider.generate("Hello!")
        >>> print(response.content)
        >>> print(f"Used {response.total_tokens} tokens")
    """
    content: str
    model: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    finish_reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        """Check if the response was successful.

        Returns:
            True if content was generated, False otherwise.
        """
        return bool(self.content)


@dataclass
class Message:
    """A message in a conversation.

    Attributes:
        role: The role of the message sender (system, user, assistant).
        content: The message content.
        name: Optional name for the message sender.

    Example:
        >>> message = Message(role='user', content='Hello!')
    """
    role: str
    content: str
    name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary format.

        Returns:
            Dictionary representation of the message.
        """
        result = {"role": self.role, "content": self.content}
        if self.name:
            result["name"] = self.name
        return result


class LLMProvider(ABC):
    """Abstract base class for LLM providers.

    This class defines the interface that all LLM providers must implement.
    It provides a consistent API for generating text, managing conversations,
    and handling configuration.

    Subclasses must implement:
        - generate(): Generate text from a prompt
        - generate_chat(): Generate text from a conversation
        - validate_config(): Validate provider configuration
        - get_provider_name(): Return the provider name

    Attributes:
        config: The LLM configuration.
        _client: The underlying API client (provider-specific).

    Example:
        >>> class MyProvider(LLMProvider):
        ...     def generate(self, prompt: str) -> LLMResponse:
        ...         # Implementation here
        ...         pass
    """

    def __init__(self, config: Optional[LLMConfig] = None) -> None:
        """Initialize the LLM provider.

        Args:
            config: LLM configuration. If None, uses defaults.
        """
        self.config = config or LLMConfig()
        self._client: Any = None
        self._initialized = False
        logger.debug(f"Initializing {self.get_provider_name()} provider")

    @abstractmethod
    def generate(self, prompt: str, **kwargs: Any) -> LLMResponse:
        """Generate text from a prompt.

        Args:
            prompt: The input prompt for text generation.
            **kwargs: Additional generation parameters.

        Returns:
            LLMResponse containing the generated text.

        Raises:
            LLMError: If generation fails.
        """
        pass

    @abstractmethod
    def generate_chat(
        self,
        messages: List[Message],
        **kwargs: Any
    ) -> LLMResponse:
        """Generate a response in a chat conversation.

        Args:
            messages: List of conversation messages.
            **kwargs: Additional generation parameters.

        Returns:
            LLMResponse containing the generated response.

        Raises:
            LLMError: If generation fails.
        """
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """Validate the provider configuration.

        Returns:
            True if configuration is valid, False otherwise.
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the name of the LLM provider.

        Returns:
            String identifier for the provider.
        """
        pass

    def initialize(self) -> None:
        """Initialize the provider client.

        This method should be called before making any API calls.
        Subclasses should override to set up provider-specific clients.
        """
        if not self._initialized:
            self.validate_config()
            self._initialized = True
            logger.info(f"{self.get_provider_name()} provider initialized")

    def is_initialized(self) -> bool:
        """Check if the provider is initialized.

        Returns:
            True if initialized, False otherwise.
        """
        return self._initialized


class LLMError(Exception):
    """Exception raised for LLM-related errors.

    Attributes:
        message: Error message.
        provider: The provider that raised the error.
        original_error: The original exception, if any.

    Example:
        >>> raise LLMError("API rate limit exceeded", provider="openai")
    """

    def __init__(
        self,
        message: str,
        provider: str = "",
        original_error: Optional[Exception] = None
    ) -> None:
        """Initialize the LLM error.

        Args:
            message: Error message.
            provider: The provider name.
            original_error: The original exception.
        """
        self.message = message
        self.provider = provider
        self.original_error = original_error
        super().__init__(self.message)


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider implementation.

    This provider supports OpenAI's GPT models including GPT-4, GPT-4-turbo,
    and GPT-3.5-turbo. It uses the latest OpenAI API patterns.

    Attributes:
        SUPPORTED_MODELS: List of supported model names.

    Example:
        >>> config = LLMConfig(api_key='sk-xxx', model='gpt-4')
        >>> provider = OpenAIProvider(config)
        >>> response = provider.generate("Explain quantum computing")

    Note:
        Requires the 'openai' package to be installed.
        Install with: pip install openai>=1.0.0
    """

    SUPPORTED_MODELS = [
        "gpt-4",
        "gpt-4-turbo",
        "gpt-4-turbo-preview",
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k",
    ]

    def __init__(self, config: Optional[LLMConfig] = None) -> None:
        """Initialize the OpenAI provider.

        Args:
            config: LLM configuration.
        """
        super().__init__(config)
        self._client = None

    def initialize(self) -> None:
        """Initialize the OpenAI client.

        Raises:
            LLMError: If the openai package is not installed.
        """
        if self._initialized:
            return

        try:
            # NOTE: Using dynamic import to support optional dependency
            import openai
            self._client = openai.OpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url,
                timeout=self.config.timeout
            )
            self._initialized = True
            logger.info("OpenAI provider initialized successfully")
        except ImportError:
            logger.error("OpenAI package not installed")
            raise LLMError(
                "OpenAI package not installed. Install with: pip install openai>=1.0.0",
                provider="openai"
            )

    def generate(self, prompt: str, **kwargs: Any) -> LLMResponse:
        """Generate text from a prompt using OpenAI.

        Args:
            prompt: The input prompt.
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            LLMResponse with generated text.

        Raises:
            LLMError: If generation fails.
        """
        messages = [Message(role="user", content=prompt)]
        return self.generate_chat(messages, **kwargs)

    def generate_chat(
        self,
        messages: List[Message],
        **kwargs: Any
    ) -> LLMResponse:
        """Generate a chat response using OpenAI.

        Args:
            messages: List of conversation messages.
            **kwargs: Additional parameters.

        Returns:
            LLMResponse with generated response.

        Raises:
            LLMError: If generation fails.
        """
        if not self._initialized:
            self.initialize()

        try:
            # Merge kwargs with config
            params = {
                "model": kwargs.get("model", self.config.model),
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "top_p": kwargs.get("top_p", self.config.top_p),
                "frequency_penalty": kwargs.get("frequency_penalty", self.config.frequency_penalty),
                "presence_penalty": kwargs.get("presence_penalty", self.config.presence_penalty),
            }

            response = self._client.chat.completions.create(
                messages=[m.to_dict() for m in messages],
                **params
            )

            choice = response.choices[0]
            return LLMResponse(
                content=choice.message.content or "",
                model=response.model,
                prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
                completion_tokens=response.usage.completion_tokens if response.usage else 0,
                total_tokens=response.usage.total_tokens if response.usage else 0,
                finish_reason=choice.finish_reason or "",
                metadata={"id": response.id}
            )

        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise LLMError(
                f"OpenAI generation failed: {str(e)}",
                provider="openai",
                original_error=e
            )

    def validate_config(self) -> bool:
        """Validate OpenAI configuration.

        Returns:
            True if configuration is valid.

        Raises:
            LLMError: If configuration is invalid.
        """
        if not self.config.api_key:
            raise LLMError(
                "OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key in config.",
                provider="openai"
            )

        if self.config.model not in self.SUPPORTED_MODELS:
            logger.warning(
                f"Model '{self.config.model}' may not be supported. "
                f"Known models: {self.SUPPORTED_MODELS}"
            )

        return True

    def get_provider_name(self) -> str:
        """Get the provider name.

        Returns:
            'openai' string identifier.
        """
        return "openai"


class AnthropicProvider(LLMProvider):
    """Anthropic LLM provider implementation.

    This provider supports Anthropic's Claude models including Claude 3
    (Opus, Sonnet, Haiku) variants.

    Attributes:
        SUPPORTED_MODELS: List of supported model names.

    Example:
        >>> config = LLMConfig(api_key='xxx', model='claude-3-opus-20240229')
        >>> provider = AnthropicProvider(config)
        >>> response = provider.generate("Explain machine learning")

    Note:
        Requires the 'anthropic' package to be installed.
        Install with: pip install anthropic>=0.20.0
    """

    SUPPORTED_MODELS = [
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
        "claude-3-5-sonnet-20240620",
        "claude-2.1",
        "claude-2.0",
    ]

    def __init__(self, config: Optional[LLMConfig] = None) -> None:
        """Initialize the Anthropic provider.

        Args:
            config: LLM configuration.
        """
        super().__init__(config)
        if self.config.model == "gpt-4":
            # Set default Anthropic model if OpenAI default was used
            self.config.model = "claude-3-sonnet-20240229"
        self._client = None

    def initialize(self) -> None:
        """Initialize the Anthropic client.

        Raises:
            LLMError: If the anthropic package is not installed.
        """
        if self._initialized:
            return

        try:
            import anthropic
            api_key = self.config.api_key or os.environ.get("ANTHROPIC_API_KEY")
            self._client = anthropic.Anthropic(api_key=api_key)
            self._initialized = True
            logger.info("Anthropic provider initialized successfully")
        except ImportError:
            logger.error("Anthropic package not installed")
            raise LLMError(
                "Anthropic package not installed. Install with: pip install anthropic>=0.20.0",
                provider="anthropic"
            )

    def generate(self, prompt: str, **kwargs: Any) -> LLMResponse:
        """Generate text from a prompt using Anthropic.

        Args:
            prompt: The input prompt.
            **kwargs: Additional parameters.

        Returns:
            LLMResponse with generated text.
        """
        messages = [Message(role="user", content=prompt)]
        return self.generate_chat(messages, **kwargs)

    def generate_chat(
        self,
        messages: List[Message],
        **kwargs: Any
    ) -> LLMResponse:
        """Generate a chat response using Anthropic.

        Args:
            messages: List of conversation messages.
            **kwargs: Additional parameters.

        Returns:
            LLMResponse with generated response.

        Raises:
            LLMError: If generation fails.
        """
        if not self._initialized:
            self.initialize()

        try:
            # Separate system messages from conversation
            system_content = ""
            chat_messages = []
            for msg in messages:
                if msg.role == "system":
                    system_content += msg.content + "\n"
                else:
                    chat_messages.append(msg.to_dict())

            params = {
                "model": kwargs.get("model", self.config.model),
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "messages": chat_messages,
            }

            if system_content:
                params["system"] = system_content.strip()

            response = self._client.messages.create(**params)

            return LLMResponse(
                content=response.content[0].text if response.content else "",
                model=response.model,
                prompt_tokens=response.usage.input_tokens if response.usage else 0,
                completion_tokens=response.usage.output_tokens if response.usage else 0,
                total_tokens=(
                    (response.usage.input_tokens + response.usage.output_tokens)
                    if response.usage else 0
                ),
                finish_reason=response.stop_reason or "",
                metadata={"id": response.id}
            )

        except Exception as e:
            logger.error(f"Anthropic generation failed: {e}")
            raise LLMError(
                f"Anthropic generation failed: {str(e)}",
                provider="anthropic",
                original_error=e
            )

    def validate_config(self) -> bool:
        """Validate Anthropic configuration.

        Returns:
            True if configuration is valid.

        Raises:
            LLMError: If configuration is invalid.
        """
        api_key = self.config.api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise LLMError(
                "Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable.",
                provider="anthropic"
            )
        return True

    def get_provider_name(self) -> str:
        """Get the provider name.

        Returns:
            'anthropic' string identifier.
        """
        return "anthropic"


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing.

    This provider returns predefined responses without making actual API calls.
    It's useful for unit testing and development.

    Attributes:
        responses: Queue of predefined responses.
        call_history: List of all calls made to the provider.

    Example:
        >>> provider = MockLLMProvider()
        >>> provider.set_response("Hello from mock!")
        >>> response = provider.generate("Hello")
        >>> assert response.content == "Hello from mock!"
    """

    def __init__(self, config: Optional[LLMConfig] = None) -> None:
        """Initialize the mock provider.

        Args:
            config: LLM configuration (mostly ignored for mock).
        """
        super().__init__(config)
        self.responses: List[str] = []
        self.call_history: List[Dict[str, Any]] = []
        self._initialized = True

    def set_response(self, response: str) -> None:
        """Set the next response to return.

        Args:
            response: The response text.
        """
        self.responses.append(response)

    def set_responses(self, responses: List[str]) -> None:
        """Set multiple responses to return in order.

        Args:
            responses: List of response texts.
        """
        self.responses.extend(responses)

    def generate(self, prompt: str, **kwargs: Any) -> LLMResponse:
        """Generate a mock response.

        Args:
            prompt: The input prompt.
            **kwargs: Additional parameters (ignored).

        Returns:
            LLMResponse with mock content.
        """
        self.call_history.append({
            "type": "generate",
            "prompt": prompt,
            "kwargs": kwargs
        })

        content = self.responses.pop(0) if self.responses else f"Mock response to: {prompt}"

        return LLMResponse(
            content=content,
            model="mock-model",
            prompt_tokens=len(prompt.split()),
            completion_tokens=len(content.split()),
            total_tokens=len(prompt.split()) + len(content.split()),
            finish_reason="stop"
        )

    def generate_chat(
        self,
        messages: List[Message],
        **kwargs: Any
    ) -> LLMResponse:
        """Generate a mock chat response.

        Args:
            messages: List of conversation messages.
            **kwargs: Additional parameters (ignored).

        Returns:
            LLMResponse with mock content.
        """
        self.call_history.append({
            "type": "generate_chat",
            "messages": [m.to_dict() for m in messages],
            "kwargs": kwargs
        })

        content = self.responses.pop(0) if self.responses else "Mock chat response"

        return LLMResponse(
            content=content,
            model="mock-model",
            prompt_tokens=sum(len(m.content.split()) for m in messages),
            completion_tokens=len(content.split()),
            total_tokens=sum(len(m.content.split()) for m in messages) + len(content.split()),
            finish_reason="stop"
        )

    def validate_config(self) -> bool:
        """Validate mock configuration (always valid).

        Returns:
            True always.
        """
        return True

    def get_provider_name(self) -> str:
        """Get the provider name.

        Returns:
            'mock' string identifier.
        """
        return "mock"

    def clear_history(self) -> None:
        """Clear the call history."""
        self.call_history.clear()


def create_provider(
    provider_name: str,
    config: Optional[LLMConfig] = None
) -> LLMProvider:
    """Factory function to create LLM providers.

    This factory function creates the appropriate LLM provider based on the
    provider name. It supports 'openai', 'anthropic', and 'mock' providers.

    Args:
        provider_name: The name of the provider ('openai', 'anthropic', 'mock').
        config: Optional LLM configuration.

    Returns:
        An instance of the requested LLM provider.

    Raises:
        ValueError: If the provider name is not recognized.

    Example:
        >>> provider = create_provider('openai', LLMConfig(api_key='xxx'))
        >>> response = provider.generate("Hello!")
    """
    providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "mock": MockLLMProvider,
    }

    if provider_name.lower() not in providers:
        raise ValueError(
            f"Unknown provider '{provider_name}'. "
            f"Available providers: {list(providers.keys())}"
        )

    provider_class = providers[provider_name.lower()]
    return provider_class(config)


# HACK: Legacy support for old langchain-style imports
# TODO(deprecation): Remove in version 2.0
LLMChain = None  # Placeholder for backward compatibility
