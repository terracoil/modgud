"""Port definition for factories that create pipeable objects."""

from typing import Any, Callable, Protocol, TypeVar, runtime_checkable

from .pipeable_port import PipeablePort

T = TypeVar('T')


@runtime_checkable
class PipeableFactoryPort(Protocol):
  """Interface for factories that create pipeable objects."""

  def create_pipeable(self, func: Callable[..., Any]) -> PipeablePort:
    """
    Create a pipeable wrapper around a function.

    Args:
        func: The function to make pipeable

    Returns:
        PipeablePort: Pipeable wrapper around the function

    """
    ...

  def pipeable_decorator(self, func: Callable[..., T]) -> PipeablePort:
    """
    Decorator that makes functions pipeable via | operator.

    Args:
        func: The function to make pipeable

    Returns:
        A Pipeable wrapper around the function

    """
    ...
