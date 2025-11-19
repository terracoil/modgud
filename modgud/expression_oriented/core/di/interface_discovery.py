"""
Interface discovery for automatic service registration.

This module provides the InterfaceDiscovery class that automatically discovers
interface implementations following the single class per file principle.
"""

import importlib
import inspect
import pkgutil
from abc import ABC
from typing import Any, Dict, List, Optional, Set, Type


class InterfaceDiscovery:
  """
  Discovers interface implementations for automatic service registration.

  Scans modules to find classes that implement interfaces (Protocols or ABCs)
  and supports naming convention-based default selection.
  """

  def __init__(self) -> None:
    """Initialize the interface discovery."""
    self._discovered_implementations: Dict[Type, List[Type]] = {}
    self._scanned_modules: Set[str] = set()

  def scan_module(self, module_name: str) -> None:
    """
    Scan a module for interface implementations.

    Args:
        module_name: Name of the module to scan (e.g., 'myapp.services')

    """
    if module_name in self._scanned_modules:
      return

    try:
      module = importlib.import_module(module_name)
      self._scan_module_recursive(module)
      self._scanned_modules.add(module_name)
    except ImportError:
      # Module doesn't exist or can't be imported
      pass

  def _scan_module_recursive(self, module: Any) -> None:
    """Recursively scan module for implementations."""
    # Scan current module
    self._scan_module_classes(module)

    # Scan sub-modules if it's a package
    try:
      if hasattr(module, '__path__'):
        for _, name, ispkg in pkgutil.iter_modules(module.__path__, module.__name__ + '.'):
          if name not in self._scanned_modules:
            try:
              submodule = importlib.import_module(name)
              self._scan_module_recursive(submodule)
            except ImportError:
              continue
    except (AttributeError, TypeError):
      # Not a package or can't iterate
      pass

  def _scan_module_classes(self, module: Any) -> None:
    """Scan classes in a module for interface implementations."""
    for name in dir(module):
      try:
        obj = getattr(module, name)

        # Only process classes defined in this module
        if (
          inspect.isclass(obj) and hasattr(obj, '__module__') and obj.__module__ == module.__name__
        ):
          # Find interfaces this class implements
          interfaces = self._get_implemented_interfaces(obj)

          for interface in interfaces:
            if interface not in self._discovered_implementations:
              self._discovered_implementations[interface] = []

            if obj not in self._discovered_implementations[interface]:
              self._discovered_implementations[interface].append(obj)

      except (AttributeError, TypeError):
        # Skip objects that can't be introspected
        continue

  def _get_implemented_interfaces(self, cls: Type) -> List[Type]:
    """
    Get all interfaces (Protocols/ABCs) implemented by a class.

    Args:
        cls: Class to analyze

    Returns:
        List of interface types implemented by the class

    """
    interfaces = []

    # Check MRO for Protocol and ABC base classes
    for base in cls.__mro__[1:]:  # Skip the class itself
      if self._is_interface(base):
        interfaces.append(base)

    return interfaces

  def _is_interface(self, cls: Type) -> bool:
    """
    Check if a class is an interface (Protocol or ABC).

    Args:
        cls: Class to check

    Returns:
        True if the class is an interface

    """
    # Check if it's a Protocol
    if hasattr(cls, '_is_protocol') and cls._is_protocol:
      return True

    # Check if it's an ABC with abstract methods
    if issubclass(cls, ABC) and getattr(cls, '__abstractmethods__', None):
      return True

    return False

  def get_implementations(self, interface: Type) -> List[Type]:
    """
    Get all discovered implementations for an interface.

    Args:
        interface: Interface type to get implementations for

    Returns:
        List of implementation classes

    """
    return self._discovered_implementations.get(interface, [])

  def get_default_implementation(self, interface: Type) -> Optional[Type]:
    """
    Get the default implementation for an interface using naming conventions.

    Prioritizes implementations with names containing:
    1. "Default"
    2. "Standard"
    3. "Common"
    4. If only one implementation exists, returns it
    5. Otherwise returns None

    Args:
        interface: Interface type to get default implementation for

    Returns:
        Default implementation class or None if no clear default

    """
    implementations = self.get_implementations(interface)

    if not implementations:
      return None

    if len(implementations) == 1:
      return implementations[0]

    # Look for naming convention defaults
    for priority_name in ['Default', 'Standard', 'Common']:
      for impl in implementations:
        if priority_name in impl.__name__:
          return impl

    # No clear default found
    return None

  def clear(self) -> None:
    """Clear all discovered implementations."""
    self._discovered_implementations.clear()
    self._scanned_modules.clear()
