"""Port definition for transformation result handling."""

from typing import Callable, Optional, Protocol, TypeVar, runtime_checkable

T = TypeVar('T')


@runtime_checkable
class TransformationResultPort(Protocol):
  """Port for transformation result handling."""

  def create_success(self, func: Callable[..., T]) -> 'TransformationResultPort':
    """Create successful transformation result."""
    ...

  def create_failure(self, error: Exception) -> 'TransformationResultPort':
    """Create failed transformation result."""
    ...

  @property
  def is_success(self) -> bool:
    """Check if transformation succeeded."""
    ...

  @property
  def function(self) -> Optional[Callable]:
    """Get transformed function if successful."""
    ...

  @property
  def error(self) -> Optional[Exception]:
    """Get error if transformation failed."""
    ...
