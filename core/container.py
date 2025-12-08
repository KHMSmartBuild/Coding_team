"""
Dependency Injection Container for the Coding Team framework.

This module provides a lightweight dependency injection container that allows
for registering and resolving dependencies across the application. It supports
singleton and factory patterns for service registration.

Example:
    >>> from core.container import Container
    >>> container = Container()
    >>> container.register('config', {'api_key': 'xxx'})
    >>> config = container.resolve('config')

Attributes:
    Container: The main dependency injection container class.

TODO(enhancement): Add support for scoped lifetimes (per-request, per-session)
TODO(enhancement): Add support for automatic dependency graph resolution
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional, Type, TypeVar, Generic

# Use standard logging with fallback
try:
    from helpers.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)

T = TypeVar('T')


class ServiceLifetime:
    """Enumeration of service lifetimes for dependency injection.

    Attributes:
        SINGLETON: Service is created once and reused for all requests.
        TRANSIENT: New service instance is created for each request.
        FACTORY: Service is created using a factory function each time.
    """
    SINGLETON = "singleton"
    TRANSIENT = "transient"
    FACTORY = "factory"


class ServiceDescriptor(Generic[T]):
    """Describes a registered service in the container.

    This class holds information about how a service should be created
    and managed by the dependency injection container.

    Attributes:
        service_type: The type or interface of the service.
        implementation: The actual implementation class or instance.
        lifetime: The lifetime of the service (singleton, transient, factory).
        instance: Cached instance for singleton services.

    Example:
        >>> descriptor = ServiceDescriptor(
        ...     service_type=LLMProvider,
        ...     implementation=OpenAIProvider,
        ...     lifetime=ServiceLifetime.SINGLETON
        ... )
    """

    def __init__(
        self,
        service_type: Type[T],
        implementation: Any,
        lifetime: str = ServiceLifetime.SINGLETON
    ) -> None:
        """Initialize a service descriptor.

        Args:
            service_type: The type or interface of the service.
            implementation: The implementation class, instance, or factory.
            lifetime: The lifetime of the service.
        """
        self.service_type = service_type
        self.implementation = implementation
        self.lifetime = lifetime
        self.instance: Optional[T] = None


class Container:
    """Dependency Injection Container for managing service dependencies.

    The Container class provides a centralized location for registering
    and resolving dependencies. It supports multiple service lifetimes
    and allows for clean separation of concerns.

    Attributes:
        _services: Dictionary mapping service names to their descriptors.
        _parent: Optional parent container for hierarchical resolution.

    Example:
        >>> container = Container()
        >>> container.register('database', DatabaseConnection())
        >>> container.register_factory('logger', lambda: get_logger(__name__))
        >>> db = container.resolve('database')
        >>> logger = container.resolve('logger')

    Note:
        Thread safety is not guaranteed. For multi-threaded applications,
        consider using locks or thread-local containers.
    """

    def __init__(self, parent: Optional['Container'] = None) -> None:
        """Initialize the dependency injection container.

        Args:
            parent: Optional parent container for hierarchical resolution.
                    If a service is not found in this container, the parent
                    will be consulted.
        """
        self._services: Dict[str, ServiceDescriptor] = {}
        self._parent = parent
        logger.debug("Container initialized")

    def register(
        self,
        name: str,
        service: Any,
        lifetime: str = ServiceLifetime.SINGLETON
    ) -> 'Container':
        """Register a service in the container.

        This method registers a service instance or class with the container.
        The service can later be resolved by name.

        Args:
            name: The unique name for the service.
            service: The service instance, class, or factory function.
            lifetime: The lifetime of the service.

        Returns:
            The container instance for method chaining.

        Raises:
            ValueError: If the service name is empty or None.

        Example:
            >>> container.register('config', {'debug': True})
            >>> container.register('llm', OpenAIProvider, ServiceLifetime.TRANSIENT)
        """
        if not name:
            raise ValueError("Service name cannot be empty")

        descriptor = ServiceDescriptor(
            service_type=type(service) if not isinstance(service, type) else service,
            implementation=service,
            lifetime=lifetime
        )

        # If it's a singleton and an instance is provided, cache it
        if lifetime == ServiceLifetime.SINGLETON and not isinstance(service, type):
            descriptor.instance = service

        self._services[name] = descriptor
        logger.debug(f"Registered service '{name}' with lifetime '{lifetime}'")
        return self

    def register_singleton(self, name: str, service: Any) -> 'Container':
        """Register a singleton service.

        Convenience method for registering singleton services. The same
        instance will be returned for all subsequent resolve calls.

        Args:
            name: The unique name for the service.
            service: The service instance or class.

        Returns:
            The container instance for method chaining.

        Example:
            >>> container.register_singleton('database', DatabaseConnection())
        """
        return self.register(name, service, ServiceLifetime.SINGLETON)

    def register_transient(self, name: str, service_class: Type[T]) -> 'Container':
        """Register a transient service.

        A new instance will be created for each resolve call.

        Args:
            name: The unique name for the service.
            service_class: The service class to instantiate.

        Returns:
            The container instance for method chaining.

        Example:
            >>> container.register_transient('handler', RequestHandler)
        """
        return self.register(name, service_class, ServiceLifetime.TRANSIENT)

    def register_factory(
        self,
        name: str,
        factory: Callable[['Container'], T]
    ) -> 'Container':
        """Register a factory function for creating services.

        The factory function will be called each time the service is resolved,
        allowing for custom instantiation logic.

        Args:
            name: The unique name for the service.
            factory: A callable that takes the container and returns a service.

        Returns:
            The container instance for method chaining.

        Example:
            >>> container.register_factory(
            ...     'llm',
            ...     lambda c: OpenAIProvider(c.resolve('config')['api_key'])
            ... )
        """
        descriptor = ServiceDescriptor(
            service_type=type(factory),
            implementation=factory,
            lifetime=ServiceLifetime.FACTORY
        )
        self._services[name] = descriptor
        logger.debug(f"Registered factory '{name}'")
        return self

    def resolve(self, name: str) -> Any:
        """Resolve a service from the container.

        This method retrieves a registered service by name, creating a new
        instance if necessary based on the service lifetime.

        Args:
            name: The name of the service to resolve.

        Returns:
            The resolved service instance.

        Raises:
            KeyError: If the service is not registered.

        Example:
            >>> config = container.resolve('config')
            >>> llm = container.resolve('llm')
        """
        if name in self._services:
            descriptor = self._services[name]
            return self._create_instance(descriptor)

        if self._parent:
            return self._parent.resolve(name)

        logger.error(f"Service '{name}' not found in container")
        raise KeyError(f"Service '{name}' is not registered")

    def _create_instance(self, descriptor: ServiceDescriptor) -> Any:
        """Create or retrieve a service instance based on its lifetime.

        Args:
            descriptor: The service descriptor containing configuration.

        Returns:
            The service instance.
        """
        if descriptor.lifetime == ServiceLifetime.SINGLETON:
            if descriptor.instance is None:
                if isinstance(descriptor.implementation, type):
                    descriptor.instance = descriptor.implementation()
                else:
                    descriptor.instance = descriptor.implementation
            return descriptor.instance

        elif descriptor.lifetime == ServiceLifetime.TRANSIENT:
            if isinstance(descriptor.implementation, type):
                return descriptor.implementation()
            return descriptor.implementation

        elif descriptor.lifetime == ServiceLifetime.FACTORY:
            return descriptor.implementation(self)

        return descriptor.implementation

    def has(self, name: str) -> bool:
        """Check if a service is registered.

        Args:
            name: The name of the service to check.

        Returns:
            True if the service is registered, False otherwise.

        Example:
            >>> if container.has('database'):
            ...     db = container.resolve('database')
        """
        if name in self._services:
            return True
        if self._parent:
            return self._parent.has(name)
        return False

    def unregister(self, name: str) -> bool:
        """Remove a service from the container.

        Args:
            name: The name of the service to remove.

        Returns:
            True if the service was removed, False if not found.

        Example:
            >>> container.unregister('old_service')
        """
        if name in self._services:
            del self._services[name]
            logger.debug(f"Unregistered service '{name}'")
            return True
        return False

    def clear(self) -> None:
        """Remove all services from the container.

        Example:
            >>> container.clear()
        """
        self._services.clear()
        logger.debug("Container cleared")

    def create_child(self) -> 'Container':
        """Create a child container with this container as parent.

        Child containers inherit services from parent containers but can
        override them with their own registrations.

        Returns:
            A new Container instance with this container as parent.

        Example:
            >>> app_container = Container()
            >>> request_container = app_container.create_child()
        """
        return Container(parent=self)

    def __contains__(self, name: str) -> bool:
        """Support 'in' operator for checking service existence.

        Args:
            name: The name of the service to check.

        Returns:
            True if the service is registered, False otherwise.
        """
        return self.has(name)

    def __repr__(self) -> str:
        """Return a string representation of the container.

        Returns:
            A string showing the number of registered services.
        """
        return f"Container(services={len(self._services)})"


# FIXME(improvement): Consider adding async support for service resolution
# NOTE: Global container instance for convenience, but prefer explicit injection
_global_container: Optional[Container] = None


def get_global_container() -> Container:
    """Get or create the global container instance.

    This provides a convenient way to access a shared container instance
    across the application. For better testability, prefer passing
    containers explicitly.

    Returns:
        The global Container instance.

    Example:
        >>> container = get_global_container()
        >>> container.register('config', app_config)
    """
    global _global_container
    if _global_container is None:
        _global_container = Container()
    return _global_container


def reset_global_container() -> None:
    """Reset the global container instance.

    This is primarily useful for testing to ensure a clean state
    between test cases.

    Example:
        >>> reset_global_container()  # Clear all registrations
    """
    global _global_container
    if _global_container:
        _global_container.clear()
    _global_container = None
