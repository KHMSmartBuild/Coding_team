"""
Tests for the Dependency Injection Container module.

This module contains unit tests for the Container class and related
dependency injection functionality.
"""

import pytest
from core.container import (
    Container,
    ServiceLifetime,
    ServiceDescriptor,
    get_global_container,
    reset_global_container,
)


class TestServiceLifetime:
    """Test suite for ServiceLifetime constants."""

    def test_lifetime_values(self):
        """Test that lifetime constants have expected values."""
        assert ServiceLifetime.SINGLETON == "singleton"
        assert ServiceLifetime.TRANSIENT == "transient"
        assert ServiceLifetime.FACTORY == "factory"


class TestContainer:
    """Test suite for Container class."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset global container before each test."""
        reset_global_container()
        yield
        reset_global_container()

    def test_container_initialization(self):
        """Test that container initializes correctly."""
        container = Container()
        assert container is not None
        assert len(container._services) == 0

    def test_register_singleton(self):
        """Test registering a singleton service."""
        container = Container()
        test_value = {"key": "value"}
        container.register("config", test_value)

        resolved = container.resolve("config")
        assert resolved == test_value
        assert resolved is test_value  # Should be same instance

    def test_register_returns_container(self):
        """Test that register returns container for chaining."""
        container = Container()
        result = container.register("test", "value")
        assert result is container

    def test_method_chaining(self):
        """Test method chaining for registration."""
        container = Container()
        container.register("a", 1).register("b", 2).register("c", 3)

        assert container.resolve("a") == 1
        assert container.resolve("b") == 2
        assert container.resolve("c") == 3

    def test_register_transient_class(self):
        """Test registering a transient class creates new instances."""

        class TestClass:
            pass

        container = Container()
        container.register_transient("test", TestClass)

        instance1 = container.resolve("test")
        instance2 = container.resolve("test")

        assert isinstance(instance1, TestClass)
        assert isinstance(instance2, TestClass)
        assert instance1 is not instance2  # Should be different instances

    def test_register_factory(self):
        """Test registering a factory function."""
        counter = [0]

        def factory(c):
            counter[0] += 1
            return f"value_{counter[0]}"

        container = Container()
        container.register_factory("test", factory)

        result1 = container.resolve("test")
        result2 = container.resolve("test")

        assert result1 == "value_1"
        assert result2 == "value_2"

    def test_resolve_nonexistent_raises_keyerror(self):
        """Test that resolving nonexistent service raises KeyError."""
        container = Container()
        with pytest.raises(KeyError) as excinfo:
            container.resolve("nonexistent")
        assert "nonexistent" in str(excinfo.value)

    def test_has_service(self):
        """Test has method returns correct values."""
        container = Container()
        container.register("exists", "value")

        assert container.has("exists") is True
        assert container.has("not_exists") is False

    def test_contains_operator(self):
        """Test __contains__ operator."""
        container = Container()
        container.register("test", "value")

        assert "test" in container
        assert "other" not in container

    def test_unregister_service(self):
        """Test unregistering a service."""
        container = Container()
        container.register("test", "value")
        assert "test" in container

        result = container.unregister("test")
        assert result is True
        assert "test" not in container

    def test_unregister_nonexistent_returns_false(self):
        """Test unregistering nonexistent service returns False."""
        container = Container()
        result = container.unregister("nonexistent")
        assert result is False

    def test_clear_container(self):
        """Test clearing all services from container."""
        container = Container()
        container.register("a", 1)
        container.register("b", 2)
        assert len(container._services) == 2

        container.clear()
        assert len(container._services) == 0

    def test_register_empty_name_raises_error(self):
        """Test that registering with empty name raises ValueError."""
        container = Container()
        with pytest.raises(ValueError):
            container.register("", "value")

    def test_register_none_name_raises_error(self):
        """Test that registering with None name raises ValueError."""
        container = Container()
        with pytest.raises(ValueError):
            container.register(None, "value")


class TestContainerHierarchy:
    """Test suite for Container parent-child relationships."""

    def test_create_child_container(self):
        """Test creating a child container."""
        parent = Container()
        child = parent.create_child()

        assert child is not parent
        assert child._parent is parent

    def test_child_resolves_from_parent(self):
        """Test that child can resolve services from parent."""
        parent = Container()
        parent.register("parent_service", "parent_value")

        child = parent.create_child()
        resolved = child.resolve("parent_service")

        assert resolved == "parent_value"

    def test_child_can_override_parent(self):
        """Test that child can override parent services."""
        parent = Container()
        parent.register("service", "parent_value")

        child = parent.create_child()
        child.register("service", "child_value")

        assert parent.resolve("service") == "parent_value"
        assert child.resolve("service") == "child_value"

    def test_child_has_checks_parent(self):
        """Test that child.has() checks parent container."""
        parent = Container()
        parent.register("parent_service", "value")

        child = parent.create_child()

        assert child.has("parent_service") is True
        assert child.has("nonexistent") is False


class TestGlobalContainer:
    """Test suite for global container functions."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset global container before each test."""
        reset_global_container()
        yield
        reset_global_container()

    def test_get_global_container(self):
        """Test getting global container."""
        container = get_global_container()
        assert container is not None
        assert isinstance(container, Container)

    def test_global_container_is_singleton(self):
        """Test that global container is a singleton."""
        container1 = get_global_container()
        container2 = get_global_container()
        assert container1 is container2

    def test_reset_global_container(self):
        """Test resetting global container."""
        container1 = get_global_container()
        container1.register("test", "value")

        reset_global_container()

        container2 = get_global_container()
        assert container1 is not container2
        assert "test" not in container2


class TestContainerRepr:
    """Test suite for Container string representations."""

    def test_repr(self):
        """Test __repr__ method."""
        container = Container()
        container.register("a", 1)
        container.register("b", 2)

        repr_str = repr(container)
        assert "Container" in repr_str
        assert "2" in repr_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
