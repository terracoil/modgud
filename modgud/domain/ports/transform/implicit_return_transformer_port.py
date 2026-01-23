"""Port definition for implicit return transformation functionality."""

from typing import Callable, Protocol, TypeVar, runtime_checkable

T = TypeVar('T')


@runtime_checkable
class ImplicitReturnTransformerPort(Protocol):
  """Port for implicit return transformation functionality."""

  def transform_function(self, func: Callable[..., T]) -> Callable[..., T]:
    """Transform function to use implicit returns.

    :param func: Function to transform
    :return: Transformed function with implicit returns
    :raises ImplicitReturnError: If transformation fails
    """
    ...

  def validate_source(self, func: Callable) -> bool:
    """Check if function source is available for transformation.

    :param func: Function to validate
    :return: True if source can be extracted and transformed
    """
    ...
