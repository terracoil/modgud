"""
Registration strategies for dependency injection.

This module provides the RegistrationStrategies class that handles different
patterns of service registration following the single class per file principle.
"""

from typing import List, Type, TypeVar

from modgud.infrastructure.di.service_container import ServiceContainer

from .interface_discovery import InterfaceDiscovery

T = TypeVar('T')


class RegistrationStrategies:
  """
  Handles different patterns of service registration.

  Provides strategies for auto-registration, manual registration,
  and convention-based registration with support for default implementations.
  """

  def __init__(self, container: ServiceContainer, discovery: InterfaceDiscovery) -> None:
    """
    Initialize registration strategies.

    Args:
        container: Service container to register services with
        discovery: Interface discovery service for finding implementations

    """
    self._container = container
    self._discovery = discovery

  def auto_register_interface(self, interface: Type[T]) -> bool:
    """
    Auto-register implementations for an interface.

    Uses the following strategy:
    1. If only one implementation exists, register it as 'default'
    2. If multiple implementations exist, register default based on naming convention
    3. Register all implementations with their class names as service names

    Args:
        interface: Interface type to auto-register implementations for

    Returns:
        True if any implementations were registered, False otherwise

    """
    implementations = self._discovery.get_implementations(interface)

    if not implementations:
      return False

    registrations_made = False

    # Register all implementations by their class names
    for impl in implementations:
      service_name = impl.__name__
      if not self._container.is_registered(interface, service_name):
        self._container.register(interface, impl, service_name)
        registrations_made = True

    # Register default implementation
    default_impl = self._discovery.get_default_implementation(interface)
    if default_impl and not self._container.is_registered(interface, 'default'):
      self._container.register(interface, default_impl, 'default')
      registrations_made = True

    return registrations_made

  def register_by_convention(self, interface: Type[T], implementation: Type[T]) -> None:
    """
    Register an implementation using naming conventions.

    Registers the implementation with multiple names based on conventions:
    - Class name
    - 'default' if name contains Default/Standard/Common
    - Lowercase class name

    Args:
        interface: Interface type
        implementation: Implementation class

    """
    class_name = implementation.__name__

    # Always register by class name
    self._container.register(interface, implementation, class_name)

    # Register as default if naming convention suggests it
    if any(keyword in class_name for keyword in ['Default', 'Standard', 'Common']):
      self._container.register(interface, implementation, 'default')

    # Register lowercase version for convenience
    lowercase_name = class_name.lower()
    if lowercase_name != class_name:
      self._container.register(interface, implementation, lowercase_name)

  def register_singleton(
    self, interface: Type[T], implementation: Type[T], name: str = 'default'
  ) -> None:
    """
    Register an implementation as a singleton.

    Args:
        interface: Interface type
        implementation: Implementation class
        name: Service name (default: 'default')

    """
    self._container.register(interface, implementation, name, singleton=True)

  def register_transient(
    self, interface: Type[T], implementation: Type[T], name: str = 'default'
  ) -> None:
    """
    Register an implementation as transient (new instance each time).

    Args:
        interface: Interface type
        implementation: Implementation class
        name: Service name (default: 'default')

    """
    self._container.register(interface, implementation, name, singleton=False)

  def bulk_auto_register(self, interfaces: List[Type]) -> int:
    """
    Auto-register implementations for multiple interfaces.

    Args:
        interfaces: List of interface types to auto-register

    Returns:
        Number of interfaces that had implementations registered

    """
    registered_count = 0

    for interface in interfaces:
      if self.auto_register_interface(interface):
        registered_count += 1

    return registered_count

  def ensure_default_registered(self, interface: Type[T]) -> bool:
    """
    Ensure a default implementation is registered for an interface.

    If no default is registered, attempts to auto-register one.

    Args:
        interface: Interface type to ensure has a default

    Returns:
        True if default is available after this call, False otherwise

    """
    # Check if default is already registered
    if self._container.is_registered(interface, 'default'):
      return True

    # Try to auto-register
    if self.auto_register_interface(interface):
      return self._container.is_registered(interface, 'default')

    return False
