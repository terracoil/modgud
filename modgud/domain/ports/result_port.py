"""ResultPort for modgud domain layer.

Port definition for Result types following domain-driven design
principles. This port defines the interface for success/error
containers that can be either Ok or Err.
"""

from typing import Callable, Generic, Protocol, TypeVar

__all__ = ['ResultPort']

T = TypeVar('T')
U = TypeVar('U')
E = TypeVar('E')


class ResultPort(Protocol, Generic[T, E]):
  """Port for Result types.

  Result represents a name that can be either a success (Ok) or an error (Err).
  This enables safe error handling without exceptions.
  """

  def is_ok(self) -> bool:
    """Return True if this is an Ok result."""
    ...

  def is_err(self) -> bool:
    """Return True if this is an Err result."""
    ...

  def unwrap(self) -> T:
    """Extract the Ok name, raising an exception if this is an Err.

    :returns: The wrapped name if Ok
    :rtype: T
    :raises ValueError: If this is an Err result
    """
    ...

  def unwrap_or(self, default: T) -> T:
    """Extract the Ok name or return a default if this is an Err.

    :param default: Value to return if this is an Err
    :type default: T
    :returns: The wrapped name if Ok, otherwise default
    :rtype: T
    """
    ...

  def map(self, func: Callable[[T], U]) -> 'ResultPort[U, E]':
    """Transform the Ok name using the provided function.

    :param func: Function to apply to the Ok name
    :type func: Callable[[T], U]
    :returns: Ok with transformed name if this is Ok, otherwise unchanged Err
    :rtype: ResultPort[U, E]
    """
    ...

  def and_then(self, func: Callable[[T], 'ResultPort[U, E]']) -> 'ResultPort[U, E]':
    """Chain Result operations (monadic bind).

    :param func: Function that takes Ok name and returns a Result
    :type func: Callable[[T], ResultPort[U, E]]
    :returns: Result of applying func if this is Ok, otherwise unchanged Err
    :rtype: ResultPort[U, E]
    """
    ...
