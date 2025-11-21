"""
EnergyInverter - Main dependency injection facade.

This module provides the EnergyInverter class that serves as the main entry point
for dependency injection operations following the single class per file principle.
"""

from typing import List, Optional, Type, TypeVar

from modgud.domain import ServiceNotFoundError

from .interface_discovery import InterfaceDiscovery
from .registration_strategies import RegistrationStrategies
from .service_container import ServiceContainer

T = TypeVar('T')


class EnergyInverter:
  """
  Main dependency injection facade.

  Provides a simple, unified interface for dependency injection operations
  including service registration, resolution, and auto-discovery.
  """

  _instance: Optional['EnergyInverter'] = None
  _container: Optional[ServiceContainer] = None
  _discovery: Optional[InterfaceDiscovery] = None
  _strategies: Optional[RegistrationStrategies] = None

  def __new__(cls) -> 'EnergyInverter':
    """Ensure singleton instance."""
    if cls._instance is None:
      cls._instance = super().__new__(cls)
      cls._instance._initialize()
    return cls._instance

  def _initialize(self) -> None:
    """Initialize the DI system components."""
    self._container = ServiceContainer()
    self._discovery = InterfaceDiscovery()
    self._strategies = RegistrationStrategies(self._container, self._discovery)

  @classmethod
  def instance(cls) -> 'EnergyInverter':
    """Get the singleton instance."""
    return cls()

  def register(self, interface: Type[T], implementation: Type[T], name: str = 'default') -> None:
    """
    Register a service implementation.

    Args:
        interface: Interface type
        implementation: Implementation class
        name: Service name (default: 'default')

    """
    # Use registration strategies for convention-based registration
    if name == 'default':
      self._strategies.register_by_convention(interface, implementation)
    else:
      self._container.register(interface, implementation, name)

  def resolve(self, interface: Type[T], name: str = 'default') -> T:
    """
    Resolve a service instance.

    Args:
        interface: Interface type to resolve
        name: Service name (default: 'default')

    Returns:
        Service instance

    Raises:
        ServiceNotFoundError: If service cannot be resolved

    """
    # Try to resolve directly first
    try:
      return self._container.resolve(interface, name)
    except ServiceNotFoundError:
      # If not found, try auto-registration
      if self._strategies.ensure_default_registered(interface):
        return self._container.resolve(interface, name)
      raise

  def scan_modules(self, *module_names: str) -> None:
    """
    Scan modules for interface implementations.

    Args:
        *module_names: Module names to scan

    """
    for module_name in module_names:
      self._discovery.scan_module(module_name)

  def auto_register(self, interface: Type[T]) -> bool:
    """
    Auto-register implementations for an interface.

    Args:
        interface: Interface type to auto-register

    Returns:
        True if implementations were registered, False otherwise

    """
    return self._strategies.auto_register_interface(interface)

  def is_registered(self, interface: Type[T], name: str = 'default') -> bool:
    """
    Check if a service is registered.

    Args:
        interface: Interface type
        name: Service name (default: 'default')

    Returns:
        True if service is registered, False otherwise

    """
    return self._container.is_registered(interface, name)

  def get_implementations(self, interface: Type[T]) -> List[Type]:
    """
    Get discovered implementations for an interface.

    Args:
        interface: Interface type

    Returns:
        List of implementation classes

    """
    return self._discovery.get_implementations(interface)

  def clear(self) -> None:
    """Clear all registrations and discoveries."""
    self._container.clear()
    self._discovery.clear()

  @classmethod
  def reset(cls) -> None:
    """Reset the singleton instance (mainly for testing)."""
    cls._instance = None
    cls._container = None
    cls._discovery = None
    cls._strategies = None
