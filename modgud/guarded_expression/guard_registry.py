"""Custom guard registration system for extending CommonGuards.

Allows external packages to register custom guard validators that can be
accessed through the CommonGuards interface or separately.
"""

from typing import Callable, Dict, Optional

from .types import GuardFunction

__all__ = [
  'GuardRegistry',
  'register_guard',
  'get_guard',
  'list_custom_guards',
  'list_guard_namespaces',
  'has_custom_guard',
  'unregister_guard',
  'get_registry',
]


class GuardRegistry:
  """Registry for custom guard validators.

  Allows registration of custom guards that can be used alongside
  CommonGuards. Guards can be registered globally or namespaced
  for organizational purposes.
  """

  def __init__(self) -> None:
    """Initialize the guard registry."""
    self._guards: Dict[str, Callable[..., GuardFunction]] = {}
    self._namespaces: Dict[str, Dict[str, Callable[..., GuardFunction]]] = {}

  def register(
    self, name: str, guard_factory: Callable[..., GuardFunction], namespace: Optional[str] = None
  ) -> None:
    """Register a custom guard validator.

    Args:
        name: Name for the guard (e.g., 'valid_file_path')
        guard_factory: Factory function that returns a GuardFunction
        namespace: Optional namespace for organization (e.g., 'cli', 'web')

    Example:
        def valid_file_path_factory(param_name: str = 'path', position: int = 0) -> GuardFunction:
            def check_file_path(*args, **kwargs) -> Union[bool, str]:
                # Implementation here
                return True
            return check_file_path

        registry.register('valid_file_path', valid_file_path_factory, namespace='cli')

    """
    if namespace is None:
      if name in self._guards:
        raise ValueError(f"Guard '{name}' is already registered in global namespace")
      self._guards[name] = guard_factory
    else:
      if namespace not in self._namespaces:
        self._namespaces[namespace] = {}
      if name in self._namespaces[namespace]:
        raise ValueError(f"Guard '{name}' is already registered in namespace '{namespace}'")
      self._namespaces[namespace][name] = guard_factory

  def get(
    self, name: str, namespace: Optional[str] = None
  ) -> Optional[Callable[..., GuardFunction]]:
    """Retrieve a registered guard factory.

    Args:
        name: Name of the guard
        namespace: Optional namespace to search in

    Returns:
        Guard factory function if found, None otherwise

    """
    return (
      self._guards.get(name) if namespace is None else self._namespaces.get(namespace, {}).get(name)
    )

  def list_guards(self, namespace: Optional[str] = None) -> list[str]:
    """List all registered guard names.

    Args:
        namespace: Optional namespace to list (None for global)

    Returns:
        List of registered guard names

    """
    return (
      list(self._guards.keys())
      if namespace is None
      else list(self._namespaces.get(namespace, {}).keys())
    )

  def list_namespaces(self) -> list[str]:
    """List all registered namespaces.

    Returns:
        List of namespace names

    """
    return list(self._namespaces.keys())

  def has_guard(self, name: str, namespace: Optional[str] = None) -> bool:
    """Check if a guard is registered.

    Args:
        name: Name of the guard
        namespace: Optional namespace to check

    Returns:
        True if guard exists, False otherwise

    """
    return self.get(name, namespace) is not None

  def unregister(self, name: str, namespace: Optional[str] = None) -> bool:
    """Unregister a custom guard.

    Args:
        name: Name of the guard to remove
        namespace: Optional namespace

    Returns:
        True if guard was removed, False if not found

    """
    removed = False
    if namespace is None:
      if name in self._guards:
        del self._guards[name]
        removed = True
    else:
      if namespace in self._namespaces and name in self._namespaces[namespace]:
        del self._namespaces[namespace][name]
        if not self._namespaces[namespace]:
          del self._namespaces[namespace]
        removed = True
    return removed


# Global registry instance
_global_registry = GuardRegistry()


def register_guard(
  name: str, guard_factory: Callable[..., GuardFunction], namespace: Optional[str] = None
) -> None:
  """Register a custom guard validator in the global registry.

  This is a convenience function for accessing the global registry.

  Args:
      name: Name for the guard (e.g., 'valid_file_path')
      guard_factory: Factory function that returns a GuardFunction
      namespace: Optional namespace for organization

  Example:
      from pathlib import Path
      from modgud import register_guard

      def valid_file_path(param_name: str = 'path', position: int = 0):
          def check_file_path(*args, **kwargs):
              # Extract parameter value
              value = args[position] if position < len(args) else kwargs.get(param_name)
              if value is None:
                  return f"{param_name} is required"

              path = Path(value)
              if not path.exists():
                  return f"{param_name} does not exist: {value}"
              if not path.is_file():
                  return f"{param_name} is not a file: {value}"

              return True
          return check_file_path

      # Register the guard
      register_guard('valid_file_path', valid_file_path, namespace='filesystem')

      # Use it with guarded_expression
      from modgud import guarded_expression, get_guard

      @guarded_expression(
          get_guard('valid_file_path', namespace='filesystem')('config_file'),
          log=True
      )
      def load_config(config_file: str):
          with open(config_file) as f:
              return f.read()

  """
  _global_registry.register(name, guard_factory, namespace)


def get_guard(name: str, namespace: Optional[str] = None) -> Optional[Callable[..., GuardFunction]]:
  """Retrieve a registered guard factory from the global registry.

  Args:
      name: Name of the guard
      namespace: Optional namespace

  Returns:
      Guard factory function if found, None otherwise

  """
  return _global_registry.get(name, namespace)


def list_custom_guards(namespace: Optional[str] = None) -> list[str]:
  """List all registered custom guards.

  Args:
      namespace: Optional namespace to list

  Returns:
      List of registered guard names

  """
  return _global_registry.list_guards(namespace)


def list_guard_namespaces() -> list[str]:
  """List all registered guard namespaces.

  Returns:
      List of namespace names

  """
  return _global_registry.list_namespaces()


def has_custom_guard(name: str, namespace: Optional[str] = None) -> bool:
  """Check if a custom guard is registered.

  Args:
      name: Name of the guard
      namespace: Optional namespace

  Returns:
      True if guard exists, False otherwise

  """
  return _global_registry.has_guard(name, namespace)


def unregister_guard(name: str, namespace: Optional[str] = None) -> bool:
  """Unregister a custom guard from the global registry.

  Args:
      name: Name of the guard
      namespace: Optional namespace

  Returns:
      True if guard was removed, False if not found

  """
  return _global_registry.unregister(name, namespace)


def get_registry() -> GuardRegistry:
  """Get the global guard registry instance.

  Returns:
      Global GuardRegistry instance

  """
  return _global_registry
