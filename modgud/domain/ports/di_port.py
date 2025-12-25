"""Port definitions for dependency injection functionality."""

from typing import Any, Callable, Dict, Protocol, Type, TypeVar, runtime_checkable

T = TypeVar('T')


@runtime_checkable
class DIContainerPort(Protocol):
  """Port for dependency injection container operations."""

  def resolve(self, interface_type: Type[T], name: str = 'default') -> T:
    """
    Resolve a dependency by interface type.

    :param interface_type: The interface/protocol type to resolve
    :param name: Named instance identifier
    :return: The resolved implementation instance
    :raises KeyError: If no implementation is registered
    """
    ...

  def register(self, interface_type: Type[T], implementation: T, name: str = 'default') -> None:
    """
    Register an implementation for an interface.

    :param interface_type: The interface/protocol type
    :param implementation: The implementation instance
    :param name: Named instance identifier
    """
    ...

  def has_registration(self, interface_type: Type[T], name: str = 'default') -> bool:
    """
    Check if an implementation is registered.

    :param interface_type: The interface/protocol type
    :param name: Named instance identifier
    :return: True if registered, False otherwise
    """
    ...

  def clear_registrations(self) -> None:
    """Clear all registered implementations."""
    ...


@runtime_checkable
class InjectableDetectorPort(Protocol):
  """Port for detecting injectable parameters."""

  def is_injectable(self, param_type: Any) -> bool:
    """
    Determine if a type should be dependency injected.

    :param param_type: The parameter type annotation
    :return: True if the type should be injected
    """
    ...

  def get_injectable_params(self, func: Callable) -> Dict[str, Type]:
    """
    Extract injectable parameters from a function signature.

    :param func: Function to analyze
    :return: Dictionary mapping parameter names to their types
    """
    ...

  def is_protocol(self, param_type: Any) -> bool:
    """
    Check if a type is a Protocol.

    :param param_type: The type to check
    :return: True if it's a Protocol
    """
    ...


@runtime_checkable
class DependencyResolverPort(Protocol):
  """Port for dependency resolution logic."""

  def resolve_dependencies(self, func: Callable, container: DIContainerPort) -> Dict[str, Any]:
    """
    Resolve all dependencies for a function.

    :param func: Function with dependencies
    :param container: DI container to resolve from
    :return: Dictionary mapping parameter names to resolved instances
    """
    ...

  def create_injection_wrapper(self, func: Callable, container: DIContainerPort) -> Callable:
    """
    Create a wrapper that injects dependencies.

    :param func: Function to wrap
    :param container: DI container to use
    :return: Wrapped function with automatic injection
    """
    ...


@runtime_checkable
class InjectionMapBuilderPort(Protocol):
  """Port for building injection parameter maps."""

  def build_injection_map(
    self, func: Callable, detector: InjectableDetectorPort
  ) -> Dict[str, Type]:
    """
    Build a map of parameters that need injection.

    :param func: Function to analyze
    :param detector: Injectable detector to use
    :return: Map of parameter names to types
    """
    ...

  def merge_with_provided(
    self, injection_map: Dict[str, Type], provided_args: tuple, provided_kwargs: dict
  ) -> Dict[str, Type]:
    """
    Remove already-provided parameters from injection map.

    :param injection_map: Full injection map
    :param provided_args: Positional arguments provided
    :param provided_kwargs: Keyword arguments provided
    :return: Filtered injection map
    """
    ...
