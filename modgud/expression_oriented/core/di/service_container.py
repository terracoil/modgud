"""
Service container for dependency injection.

This module provides the ServiceContainer class that manages service registration,
resolution, and lifecycle following the single class per file principle.
"""

import threading
from collections import defaultdict
from typing import Any, Callable, Dict, Type, TypeVar, Union

T = TypeVar('T')


class ServiceContainer:
  """
  Thread-safe service container for dependency injection.

  Manages service registration, resolution, and lifecycle with support for:
  - Interface-based registration
  - Named service registration
  - Singleton and transient lifetimes
  - Auto-discovery of implementations
  - Default implementation selection
  """

  def __init__(self) -> None:
    """Initialize the service container."""
    self._services: Dict[Type, Dict[str, Any]] = defaultdict(dict)
    self._instances: Dict[Type, Dict[str, Any]] = defaultdict(dict)
    self._lock = threading.RLock()

  def register(
    self,
    interface: Type[T],
    implementation: Union[Type[T], Callable[[], T]],
    name: str = 'default',
    singleton: bool = True,
  ) -> None:
    """
    Register a service implementation for an interface.

    Args:
        interface: The interface/protocol type
        implementation: The implementation class or factory function
        name: Service name (default: 'default')
        singleton: If True, creates single instance (default: True)

    """
    with self._lock:
      if interface not in self._services:
        self._services[interface] = {}

      self._services[interface][name] = {'implementation': implementation, 'singleton': singleton}

      # Clear cached instance if re-registering
      if interface in self._instances and name in self._instances[interface]:
        del self._instances[interface][name]

  def resolve(self, interface: Type[T], name: str = 'default') -> T:
    """
    Resolve a service instance for the given interface.

    Args:
        interface: The interface/protocol type to resolve
        name: Service name to resolve (default: 'default')

    Returns:
        Service instance

    Raises:
        ServiceNotFoundError: If no service is registered for the interface/name

    """
    with self._lock:
      # Check if service is registered
      if interface not in self._services or name not in self._services[interface]:
        raise ServiceNotFoundError(
          f"No service registered for {interface.__name__} with name '{name}'"
        )

      service_config = self._services[interface][name]

      # Return cached singleton instance if available
      if service_config['singleton']:
        if interface in self._instances and name in self._instances[interface]:
          return self._instances[interface][name]

      # Create new instance
      implementation = service_config['implementation']

      if callable(implementation) and not isinstance(implementation, type):
        # Factory function
        instance = implementation()
      else:
        # Class constructor
        instance = implementation()

      # Cache singleton instance
      if service_config['singleton']:
        if interface not in self._instances:
          self._instances[interface] = {}
        self._instances[interface][name] = instance

      return instance

  def is_registered(self, interface: Type[T], name: str = 'default') -> bool:
    """
    Check if a service is registered for the given interface and name.

    Args:
        interface: The interface/protocol type
        name: Service name (default: 'default')

    Returns:
        True if service is registered, False otherwise

    """
    with self._lock:
      return interface in self._services and name in self._services[interface]

  def get_registered_names(self, interface: Type[T]) -> list[str]:
    """
    Get all registered service names for an interface.

    Args:
        interface: The interface/protocol type

    Returns:
        List of registered service names

    """
    with self._lock:
      if interface not in self._services:
        return []
      return list(self._services[interface].keys())

  def clear(self) -> None:
    """Clear all registered services and cached instances."""
    with self._lock:
      self._services.clear()
      self._instances.clear()


class ServiceNotFoundError(Exception):
  """Raised when a requested service cannot be found in the container."""

  pass
