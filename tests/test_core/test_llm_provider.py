"""
Tests for the LLM Provider module.

This module contains unit tests for the LLMProvider classes,
LLMConfig, and related functionality.
"""

import pytest
from core.llm_provider import (
    LLMConfig,
    LLMResponse,
    Message,
    LLMProvider,
    LLMError,
    MockLLMProvider,
    create_provider,
)


class TestLLMConfig:
    """Test suite for LLMConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = LLMConfig()
        assert config.model == "gpt-4"
        assert config.temperature == 0.7
        assert config.max_tokens == 4096
        assert config.top_p == 1.0
        assert config.timeout == 60

    def test_custom_config(self):
        """Test custom configuration values."""
        config = LLMConfig(
            api_key="test_key",
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=1000
        )
        assert config.api_key == "test_key"
        assert config.model == "gpt-3.5-turbo"
        assert config.temperature == 0.5
        assert config.max_tokens == 1000

    def test_temperature_clamping_high(self):
        """Test that high temperature is clamped."""
        config = LLMConfig(temperature=5.0)
        assert config.temperature == 2.0

    def test_temperature_clamping_low(self):
        """Test that negative temperature is clamped."""
        config = LLMConfig(temperature=-1.0)
        assert config.temperature == 0.0

    def test_extra_params(self):
        """Test extra_params dictionary."""
        config = LLMConfig(extra_params={"custom": "value"})
        assert config.extra_params["custom"] == "value"


class TestLLMResponse:
    """Test suite for LLMResponse dataclass."""

    def test_default_response(self):
        """Test default response values."""
        response = LLMResponse(content="Hello")
        assert response.content == "Hello"
        assert response.model == ""
        assert response.prompt_tokens == 0
        assert response.completion_tokens == 0
        assert response.total_tokens == 0

    def test_full_response(self):
        """Test response with all fields."""
        response = LLMResponse(
            content="Generated text",
            model="gpt-4",
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30,
            finish_reason="stop",
            metadata={"id": "123"}
        )
        assert response.content == "Generated text"
        assert response.model == "gpt-4"
        assert response.total_tokens == 30
        assert response.metadata["id"] == "123"

    def test_success_property_true(self):
        """Test success property returns True for non-empty content."""
        response = LLMResponse(content="Some content")
        assert response.success is True

    def test_success_property_false(self):
        """Test success property returns False for empty content."""
        response = LLMResponse(content="")
        assert response.success is False


class TestMessage:
    """Test suite for Message dataclass."""

    def test_message_creation(self):
        """Test basic message creation."""
        msg = Message(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.name is None

    def test_message_with_name(self):
        """Test message with name."""
        msg = Message(role="assistant", content="Hi", name="bot")
        assert msg.name == "bot"

    def test_to_dict(self):
        """Test message to dictionary conversion."""
        msg = Message(role="user", content="Hello")
        d = msg.to_dict()
        assert d == {"role": "user", "content": "Hello"}

    def test_to_dict_with_name(self):
        """Test message to dictionary with name."""
        msg = Message(role="user", content="Hello", name="john")
        d = msg.to_dict()
        assert d == {"role": "user", "content": "Hello", "name": "john"}


class TestMockLLMProvider:
    """Test suite for MockLLMProvider class."""

    def test_initialization(self):
        """Test mock provider initialization."""
        provider = MockLLMProvider()
        assert provider.is_initialized() is True
        assert provider.get_provider_name() == "mock"

    def test_generate_default_response(self):
        """Test generate with default mock response."""
        provider = MockLLMProvider()
        response = provider.generate("Hello")
        assert "Hello" in response.content
        assert response.success is True

    def test_generate_custom_response(self):
        """Test generate with custom mock response."""
        provider = MockLLMProvider()
        provider.set_response("Custom response")

        response = provider.generate("Any prompt")
        assert response.content == "Custom response"

    def test_generate_multiple_responses(self):
        """Test multiple custom responses in order."""
        provider = MockLLMProvider()
        provider.set_responses(["First", "Second", "Third"])

        assert provider.generate("1").content == "First"
        assert provider.generate("2").content == "Second"
        assert provider.generate("3").content == "Third"

    def test_call_history(self):
        """Test that calls are recorded in history."""
        provider = MockLLMProvider()
        provider.generate("First prompt")
        provider.generate("Second prompt")

        assert len(provider.call_history) == 2
        assert provider.call_history[0]["prompt"] == "First prompt"
        assert provider.call_history[1]["prompt"] == "Second prompt"

    def test_generate_chat(self):
        """Test generate_chat method."""
        provider = MockLLMProvider()
        provider.set_response("Chat response")

        messages = [
            Message(role="system", content="You are helpful"),
            Message(role="user", content="Hello")
        ]

        response = provider.generate_chat(messages)
        assert response.content == "Chat response"

    def test_chat_history_recorded(self):
        """Test that chat calls are recorded."""
        provider = MockLLMProvider()
        messages = [Message(role="user", content="Test")]

        provider.generate_chat(messages)

        assert len(provider.call_history) == 1
        assert provider.call_history[0]["type"] == "generate_chat"

    def test_clear_history(self):
        """Test clearing call history."""
        provider = MockLLMProvider()
        provider.generate("Test")
        assert len(provider.call_history) == 1

        provider.clear_history()
        assert len(provider.call_history) == 0

    def test_validate_config(self):
        """Test validate_config always returns True."""
        provider = MockLLMProvider()
        assert provider.validate_config() is True


class TestLLMError:
    """Test suite for LLMError exception."""

    def test_error_creation(self):
        """Test basic error creation."""
        error = LLMError("Test error")
        assert str(error) == "Test error"
        assert error.message == "Test error"

    def test_error_with_provider(self):
        """Test error with provider name."""
        error = LLMError("API error", provider="openai")
        assert error.provider == "openai"

    def test_error_with_original_error(self):
        """Test error with original exception."""
        original = ValueError("Original error")
        error = LLMError("Wrapper", original_error=original)
        assert error.original_error is original


class TestCreateProvider:
    """Test suite for create_provider factory function."""

    def test_create_mock_provider(self):
        """Test creating mock provider."""
        provider = create_provider("mock")
        assert isinstance(provider, MockLLMProvider)

    def test_create_mock_provider_case_insensitive(self):
        """Test provider name is case insensitive."""
        provider = create_provider("MOCK")
        assert isinstance(provider, MockLLMProvider)

    def test_create_unknown_provider_raises_error(self):
        """Test that unknown provider raises ValueError."""
        with pytest.raises(ValueError) as excinfo:
            create_provider("unknown_provider")
        assert "Unknown provider" in str(excinfo.value)

    def test_create_provider_with_config(self):
        """Test creating provider with config."""
        config = LLMConfig(model="test-model")
        provider = create_provider("mock", config)
        assert provider.config.model == "test-model"


class TestProviderTokenCounting:
    """Test suite for token counting in providers."""

    def test_mock_provider_token_counting(self):
        """Test that mock provider counts tokens."""
        provider = MockLLMProvider()
        response = provider.generate("one two three")

        # Mock counts words as tokens
        assert response.prompt_tokens == 3  # "one two three"
        assert response.total_tokens > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
