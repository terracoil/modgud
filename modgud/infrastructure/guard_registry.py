"""
Custom guard registration system for extending CommonGuards.

Allows external packages to register custom guard validators that can be
accessed through the CommonGuards interface or separately.
"""

from typing import Callable, Dict, Optional

from ..domain.types import GuardFunction


class GuardRegistry:
  """
  Singleton registry for custom guard validators.

  Allows registration of custom guards that can be used alongside
  CommonGuards. Guards can be registered globally or namespaced
  for organizational purposes.

  Usage:
      # Direct class method access (recommended)
      GuardRegistry.register('my_guard', factory_fn)
      guard = GuardRegistry.get('my_guard')

      # Or get the singleton instance for advanced usage
      registry = GuardRegistry.instance()
      registry.register('another_guard', factory_fn)
  """

  _instance: Optional['GuardRegistry'] = None
  _allow_direct_instantiation: bool = False

  def __init__(self) -> None:
    """
    Initialize the guard registry.

    For production code, use GuardRegistry.instance() to get the singleton.
    Direct instantiation is allowed only for testing purposes.
    """
    if not GuardRegistry._allow_direct_instantiation and GuardRegistry._instance is not None:
      raise RuntimeError(
        'GuardRegistry is a singleton. Use GuardRegistry.instance() or '
        'GuardRegistry._create_for_testing() for tests.'
      )
    self._guards: Dict[str, Callable[..., GuardFunction]] = {}
    self._namespaces: Dict[str, Dict[str, Callable[..., GuardFunction]]] = {}

  @classmethod
  def _create_for_testing(cls) -> 'GuardRegistry':
    """
    Create a new GuardRegistry instance for testing.

    This bypasses the singleton enforcement to allow isolated test instances.

    Returns:
        New GuardRegistry instance for testing

    """
    cls._allow_direct_instantiation = True
    instance = cls()
    cls._allow_direct_instantiation = False
    return instance

  @classmethod
  def instance(cls) -> 'GuardRegistry':
    """
    Get the singleton GuardRegistry instance.

    Returns:
        Global GuardRegistry singleton instance

    """
    if cls._instance is None:
      cls._instance = cls.__new__(cls)
      cls._instance._guards = {}
      cls._instance._namespaces = {}
    return cls._instance

  @classmethod
  def register(
    cls, name: str, guard_factory: Callable[..., GuardFunction], namespace: Optional[str] = None
  ) -> None:
    """
    Register a custom guard validator.

    Args:
        name: Name for the guard (e.g., 'valid_file_path')
        guard_factory: Factory function that returns a GuardFunction
        namespace: Optional namespace for organization

    Example:
        GuardRegistry.register('valid_email', email_validator_factory)

    """
    cls.instance()._register(name, guard_factory, namespace)

  @classmethod
  def get(
    cls, name: str, namespace: Optional[str] = None
  ) -> Optional[Callable[..., GuardFunction]]:
    """
    Retrieve a registered guard factory.

    Args:
        name: Name of the guard
        namespace: Optional namespace

    Returns:
        Guard factory function if found, None otherwise

    """
    return cls.instance()._get(name, namespace)

  @classmethod
  def list_guards(cls, namespace: Optional[str] = None) -> list[str]:
    """
    List all registered guard names.

    Args:
        namespace: Optional namespace to list

    Returns:
        List of registered guard names

    """
    return cls.instance()._list_guards(namespace)

  @classmethod
  def list_namespaces(cls) -> list[str]:
    """
    List all registered namespaces.

    Returns:
        List of namespace names

    """
    return cls.instance()._list_namespaces()

  @classmethod
  def has_guard(cls, name: str, namespace: Optional[str] = None) -> bool:
    """
    Check if a guard is registered.

    Args:
        name: Name of the guard
        namespace: Optional namespace

    Returns:
        True if guard exists, False otherwise

    """
    return cls.instance()._has_guard(name, namespace)

  @classmethod
  def unregister(cls, name: str, namespace: Optional[str] = None) -> bool:
    """
    Unregister a custom guard.

    Args:
        name: Name of the guard
        namespace: Optional namespace

    Returns:
        True if guard was removed, False if not found

    """
    return cls.instance()._unregister(name, namespace)

  # Instance methods (prefixed with _ to indicate they're called via class methods)
  def _register(
    self, name: str, guard_factory: Callable[..., GuardFunction], namespace: Optional[str] = None
  ) -> None:
    """Instance method for registration logic."""
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

  def _get(
    self, name: str, namespace: Optional[str] = None
  ) -> Optional[Callable[..., GuardFunction]]:
    """Instance method for retrieval logic."""
    return (
      self._guards.get(name) if namespace is None else self._namespaces.get(namespace, {}).get(name)
    )

  def _list_guards(self, namespace: Optional[str] = None) -> list[str]:
    """Instance method for listing guards."""
    return (
      list(self._guards.keys())
      if namespace is None
      else list(self._namespaces.get(namespace, {}).keys())
    )

  def _list_namespaces(self) -> list[str]:
    """Instance method for listing namespaces."""
    return list(self._namespaces.keys())

  def _has_guard(self, name: str, namespace: Optional[str] = None) -> bool:
    """Instance method for checking guard existence."""
    return self._get(name, namespace) is not None

  def _unregister(self, name: str, namespace: Optional[str] = None) -> bool:
    """Instance method for unregistration logic."""
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
