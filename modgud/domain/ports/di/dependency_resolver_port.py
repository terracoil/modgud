"""Port definition for dependency resolution logic."""

from typing import Any, Callable, Dict, Protocol, runtime_checkable

from .di_container_port import DIContainerPort


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
