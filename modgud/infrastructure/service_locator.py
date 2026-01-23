"""Service locator for managing dependency injection in modgud."""

from typing import Any, Callable, Dict, Optional, Type, TypeVar

T = TypeVar('T')


class ServiceLocator:
  """Central service locator for managing application dependencies.

  Provides a simple way to register and resolve services without
  coupling the app layer directly to infrastructure implementations.
  """

  _instance: Optional['ServiceLocator'] = None
  _factories: Dict[Type, Callable[[], Any]] = {}
  _services: Dict[Type, Any] = {}

  def __new__(cls) -> 'ServiceLocator':
    """Ensure singleton instance."""
    if cls._instance is None:
      cls._instance = super().__new__(cls)
    return cls._instance

  def register_factory(self, port_type: Type[T], factory: Callable[[], T]) -> None:
    """Register a factory function for a port type.

    :param port_type: The port interface type
    :param factory: Factory function that creates the service
    """
    self._factories[port_type] = factory

  def register_instance(self, port_type: Type[T], instance: T) -> None:
    """Register a service instance directly.

    :param port_type: The port interface type
    :param instance: The service instance
    """
    self._services[port_type] = instance

  def resolve(self, port_type: Type[T]) -> T:
    """Resolve a service by its port type.

    :param port_type: The port interface type to resolve
    :return: The service instance
    :raises KeyError: If no service is registered for the port
    """
    # Check if we have a cached instance
    if port_type in self._services:
      return self._services[port_type]

    # Check if we have a factory
    if port_type in self._factories:
      # Create and cache the instance
      instance = self._factories[port_type]()
      self._services[port_type] = instance
      return instance

    raise KeyError(f'No service registered for {port_type.__name__}')

  def clear(self) -> None:
    """Clear all registrations and cached instances."""
    self._factories.clear()
    self._services.clear()

  @classmethod
  def instance(cls) -> 'ServiceLocator':
    """Get the singleton instance."""
    return cls()


# Global function for easy access
def get_service_locator() -> ServiceLocator:
  """Get the global service locator instance."""
  return ServiceLocator.instance()
