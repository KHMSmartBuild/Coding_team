"""
Dependency Injection Container Module.

This module provides a lightweight dependency injection container with support
for multiple service lifetimes: singleton, transient, and factory patterns.

Example:
    >>> container = Container()
    >>> container.register_singleton("config", Config())
    >>> config = container.resolve("config")
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union

T = TypeVar("T")


class ServiceLifetime(Enum):
    """Enumeration of service lifetime options.

    Attributes:
        SINGLETON: A single instance is created and reused for all requests.
        TRANSIENT: A new instance is created for each request.
        FACTORY: A factory function is called for each request.
    """

    SINGLETON = "singleton"
    TRANSIENT = "transient"
    FACTORY = "factory"


class ServiceDescriptor:
    """Describes a registered service in the container.

    Attributes:
        lifetime: The lifetime of the service.
        service_type: The type of the service (for transient).
        instance: The singleton instance (for singleton).
        factory: The factory function (for factory).
    """

    def __init__(
        self,
        lifetime: ServiceLifetime,
        service_type: Optional[Type] = None,
        instance: Optional[Any] = None,
        factory: Optional[Callable[..., Any]] = None,
    ):
        """Initialize a ServiceDescriptor.

        Args:
            lifetime: The lifetime of the service.
            service_type: The type of the service for transient registration.
            instance: The singleton instance.
            factory: The factory function for factory registration.
        """
        self.lifetime = lifetime
        self.service_type = service_type
        self.instance = instance
        self.factory = factory


class ContainerError(Exception):
    """Exception raised for container-related errors.

    Attributes:
        message: Explanation of the error.
    """

    pass


class Container:
    """Dependency Injection Container.

    A lightweight container for managing service registration and resolution
    with support for singleton, transient, and factory lifetimes.

    Attributes:
        _services: Dictionary of registered services.
        _parent: Optional parent container for hierarchical resolution.

    Example:
        >>> container = Container()
        >>> container.register_singleton("logger", Logger())
        >>> logger = container.resolve("logger")
    """

    def __init__(self, parent: Optional["Container"] = None):
        """Initialize the Container.

        Args:
            parent: Optional parent container for hierarchical resolution.
        """
        self._services: Dict[str, ServiceDescriptor] = {}
        self._parent = parent

    def register_singleton(
        self,
        name: str,
        instance: Any,
    ) -> "Container":
        """Register a singleton service.

        A singleton service returns the same instance for all resolve calls.

        Args:
            name: The unique name for the service.
            instance: The singleton instance to register.

        Returns:
            The container instance for method chaining.

        Raises:
            ContainerError: If a service with the same name is already registered.

        Example:
            >>> container.register_singleton("config", Config())
        """
        if name in self._services:
            raise ContainerError(f"Service '{name}' is already registered")

        self._services[name] = ServiceDescriptor(
            lifetime=ServiceLifetime.SINGLETON,
            instance=instance,
        )
        return self

    def register_transient(
        self,
        name: str,
        service_type: Type[T],
    ) -> "Container":
        """Register a transient service.

        A transient service creates a new instance for each resolve call.

        Args:
            name: The unique name for the service.
            service_type: The type of the service to instantiate.

        Returns:
            The container instance for method chaining.

        Raises:
            ContainerError: If a service with the same name is already registered.

        Example:
            >>> container.register_transient("request", RequestHandler)
        """
        if name in self._services:
            raise ContainerError(f"Service '{name}' is already registered")

        self._services[name] = ServiceDescriptor(
            lifetime=ServiceLifetime.TRANSIENT,
            service_type=service_type,
        )
        return self

    def register_factory(
        self,
        name: str,
        factory: Callable[..., T],
    ) -> "Container":
        """Register a factory service.

        A factory service calls the provided function for each resolve call.

        Args:
            name: The unique name for the service.
            factory: A callable that creates the service instance.

        Returns:
            The container instance for method chaining.

        Raises:
            ContainerError: If a service with the same name is already registered.

        Example:
            >>> container.register_factory("connection", lambda: Connection(db_url))
        """
        if name in self._services:
            raise ContainerError(f"Service '{name}' is already registered")

        self._services[name] = ServiceDescriptor(
            lifetime=ServiceLifetime.FACTORY,
            factory=factory,
        )
        return self

    def resolve(self, name: str, **kwargs: Any) -> Any:
        """Resolve a service by name.

        Args:
            name: The name of the service to resolve.
            **kwargs: Additional arguments passed to transient or factory services.

        Returns:
            The resolved service instance.

        Raises:
            ContainerError: If the service is not found.

        Example:
            >>> config = container.resolve("config")
        """
        descriptor = self._services.get(name)

        if descriptor is None:
            # Try parent container
            if self._parent is not None:
                return self._parent.resolve(name, **kwargs)
            raise ContainerError(f"Service '{name}' is not registered")

        if descriptor.lifetime == ServiceLifetime.SINGLETON:
            return descriptor.instance
        elif descriptor.lifetime == ServiceLifetime.TRANSIENT:
            if descriptor.service_type is None:
                raise ContainerError(f"Service type for '{name}' is not set")
            return descriptor.service_type(**kwargs)
        elif descriptor.lifetime == ServiceLifetime.FACTORY:
            if descriptor.factory is None:
                raise ContainerError(f"Factory for '{name}' is not set")
            return descriptor.factory(**kwargs)

        raise ContainerError(f"Unknown lifetime for service '{name}'")

    def is_registered(self, name: str) -> bool:
        """Check if a service is registered.

        Args:
            name: The name of the service to check.

        Returns:
            True if the service is registered, False otherwise.

        Example:
            >>> if container.is_registered("config"):
            ...     config = container.resolve("config")
        """
        if name in self._services:
            return True
        if self._parent is not None:
            return self._parent.is_registered(name)
        return False

    def unregister(self, name: str) -> "Container":
        """Unregister a service.

        Args:
            name: The name of the service to unregister.

        Returns:
            The container instance for method chaining.

        Raises:
            ContainerError: If the service is not registered.

        Example:
            >>> container.unregister("old_service")
        """
        if name not in self._services:
            raise ContainerError(f"Service '{name}' is not registered")
        del self._services[name]
        return self

    def create_child(self) -> "Container":
        """Create a child container.

        Child containers inherit services from their parent and can override them.

        Returns:
            A new child container.

        Example:
            >>> child = container.create_child()
            >>> child.register_singleton("override", new_instance)
        """
        return Container(parent=self)

    def clear(self) -> "Container":
        """Clear all registered services.

        Returns:
            The container instance for method chaining.

        Example:
            >>> container.clear()
        """
        self._services.clear()
        return self

    @property
    def services(self) -> Dict[str, ServiceDescriptor]:
        """Get all registered services.

        Returns:
            A dictionary of registered services.
        """
        return dict(self._services)

    def __contains__(self, name: str) -> bool:
        """Check if a service is registered using 'in' operator.

        Args:
            name: The name of the service to check.

        Returns:
            True if the service is registered, False otherwise.

        Example:
            >>> if "config" in container:
            ...     print("Config is registered")
        """
        return self.is_registered(name)

    def __len__(self) -> int:
        """Get the number of registered services.

        Returns:
            The number of registered services.
        """
        return len(self._services)
