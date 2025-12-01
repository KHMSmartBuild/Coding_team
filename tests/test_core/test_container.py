"""Tests for the Dependency Injection Container.

This module contains comprehensive tests for the Container class including
singleton, transient, and factory service registrations.
"""

import pytest
from core.container import (
    Container,
    ContainerError,
    ServiceDescriptor,
    ServiceLifetime,
)


class TestServiceLifetime:
    """Tests for ServiceLifetime enum."""

    def test_singleton_value(self):
        """Test singleton enum value."""
        assert ServiceLifetime.SINGLETON.value == "singleton"

    def test_transient_value(self):
        """Test transient enum value."""
        assert ServiceLifetime.TRANSIENT.value == "transient"

    def test_factory_value(self):
        """Test factory enum value."""
        assert ServiceLifetime.FACTORY.value == "factory"


class TestServiceDescriptor:
    """Tests for ServiceDescriptor class."""

    def test_singleton_descriptor(self):
        """Test creating a singleton descriptor."""
        instance = {"key": "value"}
        descriptor = ServiceDescriptor(
            lifetime=ServiceLifetime.SINGLETON,
            instance=instance,
        )
        assert descriptor.lifetime == ServiceLifetime.SINGLETON
        assert descriptor.instance == instance
        assert descriptor.service_type is None
        assert descriptor.factory is None

    def test_transient_descriptor(self):
        """Test creating a transient descriptor."""

        class MyService:
            pass

        descriptor = ServiceDescriptor(
            lifetime=ServiceLifetime.TRANSIENT,
            service_type=MyService,
        )
        assert descriptor.lifetime == ServiceLifetime.TRANSIENT
        assert descriptor.service_type == MyService
        assert descriptor.instance is None
        assert descriptor.factory is None

    def test_factory_descriptor(self):
        """Test creating a factory descriptor."""

        def create_service():
            return {"created": True}

        descriptor = ServiceDescriptor(
            lifetime=ServiceLifetime.FACTORY,
            factory=create_service,
        )
        assert descriptor.lifetime == ServiceLifetime.FACTORY
        assert descriptor.factory == create_service
        assert descriptor.instance is None
        assert descriptor.service_type is None


class TestContainer:
    """Tests for Container class."""

    def test_create_empty_container(self):
        """Test creating an empty container."""
        container = Container()
        assert len(container) == 0

    def test_register_singleton(self):
        """Test registering a singleton service."""
        container = Container()
        instance = {"config": "value"}
        container.register_singleton("config", instance)

        assert "config" in container
        assert container.is_registered("config")
        assert len(container) == 1

    def test_resolve_singleton(self):
        """Test resolving a singleton service."""
        container = Container()
        instance = {"config": "value"}
        container.register_singleton("config", instance)

        resolved = container.resolve("config")
        assert resolved is instance
        assert resolved == {"config": "value"}

    def test_singleton_returns_same_instance(self):
        """Test that singleton always returns the same instance."""
        container = Container()
        instance = {"counter": 0}
        container.register_singleton("counter", instance)

        resolved1 = container.resolve("counter")
        resolved1["counter"] += 1
        resolved2 = container.resolve("counter")

        assert resolved1 is resolved2
        assert resolved2["counter"] == 1

    def test_register_transient(self):
        """Test registering a transient service."""

        class MyService:
            def __init__(self):
                self.id = id(self)

        container = Container()
        container.register_transient("service", MyService)

        assert "service" in container
        assert container.is_registered("service")

    def test_resolve_transient(self):
        """Test resolving a transient service."""

        class MyService:
            pass

        container = Container()
        container.register_transient("service", MyService)

        resolved = container.resolve("service")
        assert isinstance(resolved, MyService)

    def test_transient_returns_new_instance(self):
        """Test that transient returns a new instance each time."""

        class MyService:
            pass

        container = Container()
        container.register_transient("service", MyService)

        resolved1 = container.resolve("service")
        resolved2 = container.resolve("service")

        assert resolved1 is not resolved2
        assert isinstance(resolved1, MyService)
        assert isinstance(resolved2, MyService)

    def test_register_factory(self):
        """Test registering a factory service."""
        counter = {"count": 0}

        def create_service():
            counter["count"] += 1
            return {"instance": counter["count"]}

        container = Container()
        container.register_factory("service", create_service)

        assert "service" in container
        assert container.is_registered("service")

    def test_resolve_factory(self):
        """Test resolving a factory service."""
        counter = {"count": 0}

        def create_service():
            counter["count"] += 1
            return {"instance": counter["count"]}

        container = Container()
        container.register_factory("service", create_service)

        resolved1 = container.resolve("service")
        resolved2 = container.resolve("service")

        assert resolved1 == {"instance": 1}
        assert resolved2 == {"instance": 2}

    def test_factory_with_kwargs(self):
        """Test factory service with kwargs."""

        def create_connection(**kwargs):
            return {"host": kwargs.get("host", "localhost")}

        container = Container()
        container.register_factory("connection", create_connection)

        resolved = container.resolve("connection", host="example.com")
        assert resolved == {"host": "example.com"}

    def test_resolve_unregistered_service_raises_error(self):
        """Test resolving an unregistered service raises error."""
        container = Container()

        with pytest.raises(ContainerError) as exc_info:
            container.resolve("unknown")

        assert "not registered" in str(exc_info.value)

    def test_register_duplicate_raises_error(self):
        """Test registering a duplicate service raises error."""
        container = Container()
        container.register_singleton("config", {})

        with pytest.raises(ContainerError) as exc_info:
            container.register_singleton("config", {})

        assert "already registered" in str(exc_info.value)

    def test_unregister_service(self):
        """Test unregistering a service."""
        container = Container()
        container.register_singleton("config", {})
        container.unregister("config")

        assert "config" not in container
        assert not container.is_registered("config")

    def test_unregister_unknown_raises_error(self):
        """Test unregistering an unknown service raises error."""
        container = Container()

        with pytest.raises(ContainerError) as exc_info:
            container.unregister("unknown")

        assert "not registered" in str(exc_info.value)

    def test_clear_container(self):
        """Test clearing all services from container."""
        container = Container()
        container.register_singleton("config", {})
        container.register_singleton("logger", {})
        container.clear()

        assert len(container) == 0
        assert "config" not in container
        assert "logger" not in container

    def test_method_chaining(self):
        """Test method chaining for container operations."""

        class ServiceA:
            pass

        class ServiceB:
            pass

        container = (
            Container()
            .register_singleton("config", {})
            .register_transient("service_a", ServiceA)
            .register_transient("service_b", ServiceB)
        )

        assert len(container) == 3

    def test_services_property(self):
        """Test services property returns copy of services."""
        container = Container()
        container.register_singleton("config", {})

        services = container.services
        assert "config" in services
        assert isinstance(services["config"], ServiceDescriptor)

        # Modifying returned dict shouldn't affect container
        services["new"] = "value"
        assert "new" not in container


class TestHierarchicalContainers:
    """Tests for hierarchical container functionality."""

    def test_create_child_container(self):
        """Test creating a child container."""
        parent = Container()
        child = parent.create_child()

        assert child._parent is parent

    def test_child_resolves_parent_service(self):
        """Test child container can resolve parent services."""
        parent = Container()
        parent.register_singleton("config", {"env": "production"})

        child = parent.create_child()
        resolved = child.resolve("config")

        assert resolved == {"env": "production"}

    def test_child_overrides_parent_service(self):
        """Test child container can override parent services."""
        parent = Container()
        parent.register_singleton("config", {"env": "production"})

        child = parent.create_child()
        child.register_singleton("config", {"env": "development"})

        parent_resolved = parent.resolve("config")
        child_resolved = child.resolve("config")

        assert parent_resolved == {"env": "production"}
        assert child_resolved == {"env": "development"}

    def test_child_is_registered_checks_parent(self):
        """Test is_registered checks parent container."""
        parent = Container()
        parent.register_singleton("config", {})

        child = parent.create_child()

        assert child.is_registered("config")
        assert "config" in child

    def test_multiple_levels_of_hierarchy(self):
        """Test multiple levels of container hierarchy."""
        root = Container()
        root.register_singleton("root_service", "root")

        level1 = root.create_child()
        level1.register_singleton("level1_service", "level1")

        level2 = level1.create_child()
        level2.register_singleton("level2_service", "level2")

        # level2 can resolve all services
        assert level2.resolve("root_service") == "root"
        assert level2.resolve("level1_service") == "level1"
        assert level2.resolve("level2_service") == "level2"

        # level1 cannot resolve level2 service
        with pytest.raises(ContainerError):
            level1.resolve("level2_service")


class TestContainerErrorHandling:
    """Tests for container error handling."""

    def test_container_error_message(self):
        """Test ContainerError contains meaningful message."""
        error = ContainerError("Test error message")
        assert str(error) == "Test error message"

    def test_resolve_with_none_service_type(self):
        """Test resolving transient with None service_type raises error."""
        container = Container()
        # Manually create a malformed descriptor
        container._services["broken"] = ServiceDescriptor(
            lifetime=ServiceLifetime.TRANSIENT,
            service_type=None,
        )

        with pytest.raises(ContainerError) as exc_info:
            container.resolve("broken")

        assert "not set" in str(exc_info.value)

    def test_resolve_with_none_factory(self):
        """Test resolving factory with None factory raises error."""
        container = Container()
        # Manually create a malformed descriptor
        container._services["broken"] = ServiceDescriptor(
            lifetime=ServiceLifetime.FACTORY,
            factory=None,
        )

        with pytest.raises(ContainerError) as exc_info:
            container.resolve("broken")

        assert "not set" in str(exc_info.value)
