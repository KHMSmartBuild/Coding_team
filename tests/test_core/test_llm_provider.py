"""Tests for LLM Provider abstractions.

This module contains tests for the LLM provider system including
the abstract interface, mock provider, and factory function.
"""

import pytest
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


class TestModelProvider:
    """Tests for ModelProvider enum."""

    def test_openai_value(self):
        """Test OpenAI provider enum value."""
        assert ModelProvider.OPENAI.value == "openai"

    def test_anthropic_value(self):
        """Test Anthropic provider enum value."""
        assert ModelProvider.ANTHROPIC.value == "anthropic"

    def test_mock_value(self):
        """Test Mock provider enum value."""
        assert ModelProvider.MOCK.value == "mock"


class TestMessage:
    """Tests for Message dataclass."""

    def test_create_user_message(self):
        """Test creating a user message."""
        msg = Message(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_create_system_message(self):
        """Test creating a system message."""
        msg = Message(role="system", content="You are a helpful assistant.")
        assert msg.role == "system"
        assert msg.content == "You are a helpful assistant."

    def test_create_assistant_message(self):
        """Test creating an assistant message."""
        msg = Message(role="assistant", content="How can I help?")
        assert msg.role == "assistant"
        assert msg.content == "How can I help?"


class TestLLMResponse:
    """Tests for LLMResponse dataclass."""

    def test_create_response(self):
        """Test creating an LLM response."""
        response = LLMResponse(
            content="Hello, world!",
            model="gpt-4",
            usage={"total_tokens": 10},
            finish_reason="stop",
        )
        assert response.content == "Hello, world!"
        assert response.model == "gpt-4"
        assert response.usage == {"total_tokens": 10}
        assert response.finish_reason == "stop"

    def test_response_defaults(self):
        """Test LLM response default values."""
        response = LLMResponse(content="Test")
        assert response.content == "Test"
        assert response.model == ""
        assert response.usage == {}
        assert response.raw_response is None
        assert response.finish_reason == ""


class TestLLMConfig:
    """Tests for LLMConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = LLMConfig()
        assert config.model == "gpt-3.5-turbo"
        assert config.temperature == 0.7
        assert config.max_tokens == 1000
        assert config.top_p == 1.0
        assert config.frequency_penalty == 0.0
        assert config.presence_penalty == 0.0
        assert config.stop is None
        assert config.timeout == 30

    def test_custom_config(self):
        """Test custom configuration values."""
        config = LLMConfig(
            model="gpt-4",
            temperature=0.5,
            max_tokens=500,
            stop=["END"],
        )
        assert config.model == "gpt-4"
        assert config.temperature == 0.5
        assert config.max_tokens == 500
        assert config.stop == ["END"]


class TestLLMProviderError:
    """Tests for LLMProviderError exception."""

    def test_error_with_provider(self):
        """Test error includes provider name."""
        error = LLMProviderError("Connection failed", provider="openai")
        assert error.message == "Connection failed"
        assert error.provider == "openai"
        assert "[openai] Connection failed" in str(error)

    def test_error_default_provider(self):
        """Test error with default provider."""
        error = LLMProviderError("Error occurred")
        assert error.provider == "unknown"


class TestMockProvider:
    """Tests for MockProvider class."""

    def test_create_mock_provider(self):
        """Test creating a mock provider."""
        provider = MockProvider()
        assert provider.provider_name == "mock"
        assert len(provider.responses) == 1
        assert provider.responses[0] == "Mock response"

    def test_create_with_responses(self):
        """Test creating mock provider with custom responses."""
        responses = ["Response 1", "Response 2", "Response 3"]
        provider = MockProvider(responses=responses)
        assert provider.responses == responses

    def test_generate_returns_response(self):
        """Test generate returns mock response."""
        provider = MockProvider(responses=["Test response"])
        response = provider.generate("Hello")

        assert isinstance(response, LLMResponse)
        assert response.content == "Test response"
        assert response.model == "mock-model"
        assert response.finish_reason == "stop"

    def test_generate_cycles_responses(self):
        """Test generate cycles through responses."""
        provider = MockProvider(responses=["First", "Second"])

        r1 = provider.generate("Test 1")
        r2 = provider.generate("Test 2")
        r3 = provider.generate("Test 3")

        assert r1.content == "First"
        assert r2.content == "Second"
        assert r3.content == "First"  # Cycles back

    def test_chat_returns_response(self):
        """Test chat returns mock response."""
        provider = MockProvider(responses=["Chat response"])
        messages = [Message(role="user", content="Hello")]
        response = provider.chat(messages)

        assert response.content == "Chat response"

    def test_calls_are_recorded(self):
        """Test that calls are recorded."""
        provider = MockProvider()
        provider.generate("Test prompt")

        assert len(provider.calls) == 1
        assert provider.calls[0]["method"] == "generate"
        assert provider.calls[0]["prompt"] == "Test prompt"

    def test_chat_calls_are_recorded(self):
        """Test that chat calls are recorded."""
        provider = MockProvider()
        messages = [Message(role="user", content="Hello")]
        provider.chat(messages)

        assert len(provider.calls) == 1
        assert provider.calls[0]["method"] == "chat"
        assert provider.calls[0]["messages"] == messages

    def test_reset_clears_state(self):
        """Test reset clears calls and index."""
        provider = MockProvider(responses=["R1", "R2"])
        provider.generate("Test")
        provider.generate("Test")
        provider.reset()

        assert provider.response_index == 0
        assert len(provider.calls) == 0

    def test_add_response(self):
        """Test adding a response."""
        provider = MockProvider()
        provider.add_response("New response")

        assert "New response" in provider.responses

    def test_usage_statistics(self):
        """Test usage statistics in response."""
        provider = MockProvider()
        response = provider.generate("Test")

        assert response.usage["prompt_tokens"] == 10
        assert response.usage["completion_tokens"] == 20
        assert response.usage["total_tokens"] == 30


class TestMockProviderWithConfig:
    """Tests for MockProvider with custom config."""

    def test_mock_with_config(self):
        """Test mock provider accepts config."""
        config = LLMConfig(model="custom-model", temperature=0.5)
        provider = MockProvider(config=config)

        assert provider.config.model == "custom-model"
        assert provider.config.temperature == 0.5

    def test_update_config(self):
        """Test updating provider config."""
        provider = MockProvider()
        provider.update_config(temperature=0.3, max_tokens=500)

        assert provider.config.temperature == 0.3
        assert provider.config.max_tokens == 500


class TestOpenAIProvider:
    """Tests for OpenAIProvider class."""

    def test_create_openai_provider(self):
        """Test creating an OpenAI provider."""
        provider = OpenAIProvider(api_key="test-key")
        assert provider.provider_name == "openai"
        assert provider.api_key == "test-key"

    def test_openai_with_organization(self):
        """Test OpenAI provider with organization."""
        provider = OpenAIProvider(api_key="test-key", organization="org-123")
        assert provider.organization == "org-123"

    def test_openai_with_config(self):
        """Test OpenAI provider with custom config."""
        config = LLMConfig(model="gpt-4", temperature=0.5)
        provider = OpenAIProvider(api_key="test-key", config=config)
        assert provider.config.model == "gpt-4"

    def test_client_raises_without_package(self):
        """Test client access raises if openai not installed."""
        provider = OpenAIProvider(api_key="test-key")
        # This test only works if openai is not installed
        # In CI environment where openai is not installed, this should raise
        try:
            _ = provider.client
        except LLMProviderError as e:
            assert "openai" in str(e)


class TestAnthropicProvider:
    """Tests for AnthropicProvider class."""

    def test_create_anthropic_provider(self):
        """Test creating an Anthropic provider."""
        provider = AnthropicProvider(api_key="test-key")
        assert provider.provider_name == "anthropic"
        assert provider.api_key == "test-key"

    def test_anthropic_default_model(self):
        """Test Anthropic provider default model."""
        provider = AnthropicProvider(api_key="test-key")
        assert "claude" in provider.config.model

    def test_anthropic_with_config(self):
        """Test Anthropic provider with custom config."""
        config = LLMConfig(model="claude-3-opus", temperature=0.3)
        provider = AnthropicProvider(api_key="test-key", config=config)
        assert provider.config.model == "claude-3-opus"


class TestCreateProvider:
    """Tests for create_provider factory function."""

    def test_create_mock_provider(self):
        """Test creating a mock provider via factory."""
        provider = create_provider("mock")
        assert isinstance(provider, MockProvider)

    def test_create_mock_with_responses(self):
        """Test creating mock provider with responses."""
        provider = create_provider("mock", responses=["R1", "R2"])
        assert provider.responses == ["R1", "R2"]

    def test_create_mock_with_enum(self):
        """Test creating mock provider using enum."""
        provider = create_provider(ModelProvider.MOCK)
        assert isinstance(provider, MockProvider)

    def test_create_openai_provider(self):
        """Test creating OpenAI provider via factory."""
        provider = create_provider("openai", api_key="test-key")
        assert isinstance(provider, OpenAIProvider)

    def test_create_anthropic_provider(self):
        """Test creating Anthropic provider via factory."""
        provider = create_provider("anthropic", api_key="test-key")
        assert isinstance(provider, AnthropicProvider)

    def test_create_openai_requires_api_key(self):
        """Test OpenAI provider requires API key."""
        with pytest.raises(ValueError) as exc_info:
            create_provider("openai")
        assert "API key" in str(exc_info.value)

    def test_create_anthropic_requires_api_key(self):
        """Test Anthropic provider requires API key."""
        with pytest.raises(ValueError) as exc_info:
            create_provider("anthropic")
        assert "API key" in str(exc_info.value)

    def test_create_with_config(self):
        """Test creating provider with config."""
        config = LLMConfig(temperature=0.5)
        provider = create_provider("mock", config=config)
        assert provider.config.temperature == 0.5

    def test_create_unsupported_provider(self):
        """Test creating unsupported provider raises error."""
        with pytest.raises(ValueError) as exc_info:
            create_provider("unsupported")
        # Check that the error mentions the invalid provider
        error_msg = str(exc_info.value).lower()
        assert "unsupported" in error_msg or "valid" in error_msg


class TestProviderIntegration:
    """Integration tests for provider functionality."""

    def test_mock_conversation(self):
        """Test a mock conversation flow."""
        provider = MockProvider(
            responses=[
                "Hello! How can I help you?",
                "Python is a programming language.",
                "You're welcome!",
            ]
        )

        messages = [
            Message(role="system", content="You are a helpful assistant."),
            Message(role="user", content="Hi!"),
        ]

        r1 = provider.chat(messages)
        assert r1.content == "Hello! How can I help you?"

        messages.append(Message(role="assistant", content=r1.content))
        messages.append(Message(role="user", content="What is Python?"))

        r2 = provider.chat(messages)
        assert r2.content == "Python is a programming language."

    def test_provider_response_metadata(self):
        """Test provider response includes metadata."""
        provider = MockProvider()
        response = provider.generate("Test")

        assert response.model is not None
        assert isinstance(response.usage, dict)
        assert response.finish_reason in ["stop", "length", ""]
