"""
ResultProtocol for modgud domain layer.

Protocol definition for Result types following domain-driven design 
principles. This protocol defines the interface for success/error 
containers that can be either Ok or Err.
"""

from typing import Callable, Generic, Protocol, TypeVar

__all__ = ['ResultProtocol']

T = TypeVar('T')
U = TypeVar('U')
E = TypeVar('E')


class ResultProtocol(Protocol, Generic[T, E]):
  """
  Protocol for Result types.

  Result represents a value that can be either a success (Ok) or an error (Err).
  This enables safe error handling without exceptions.
  """

  def is_ok(self) -> bool:
    """Return True if this is an Ok result."""
    ...

  def is_err(self) -> bool:
    """Return True if this is an Err result."""
    ...

  def unwrap(self) -> T:
    """
    Extract the Ok value, raising an exception if this is an Err.

    :returns: The wrapped value if Ok
    :rtype: T
    :raises ValueError: If this is an Err result
    """
    ...

  def unwrap_or(self, default: T) -> T:
    """
    Extract the Ok value or return a default if this is an Err.

    :param default: Value to return if this is an Err
    :type default: T
    :returns: The wrapped value if Ok, otherwise default
    :rtype: T
    """
    ...

  def map(self, func: Callable[[T], U]) -> 'ResultProtocol[U, E]':
    """
    Transform the Ok value using the provided function.

    :param func: Function to apply to the Ok value
    :type func: Callable[[T], U]
    :returns: Ok with transformed value if this is Ok, otherwise unchanged Err
    :rtype: ResultProtocol[U, E]
    """
    ...

  def and_then(self, func: Callable[[T], 'ResultProtocol[U, E]']) -> 'ResultProtocol[U, E]':
    """
    Chain Result operations (monadic bind).

    :param func: Function that takes Ok value and returns a Result
    :type func: Callable[[T], ResultProtocol[U, E]]
    :returns: Result of applying func if this is Ok, otherwise unchanged Err
    :rtype: ResultProtocol[U, E]
    """
    ...