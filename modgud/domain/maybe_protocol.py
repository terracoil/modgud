"""
MaybeProtocol for modgud domain layer.

Protocol definition for Maybe types following domain-driven design
principles. This protocol defines the interface for optional value
containers that may or may not contain a value.
"""

from typing import Callable, Generic, Protocol, TypeVar

__all__ = ['MaybeProtocol']

T = TypeVar('T')
U = TypeVar('U')


class MaybeProtocol(Protocol, Generic[T]):
  """
  Protocol for Maybe types.

  Maybe represents a value that may or may not exist, providing safe operations
  for working with optional values without null pointer exceptions.
  """

  def is_some(self) -> bool:
    """Return True if this contains a value."""
    ...

  def is_nothing(self) -> bool:
    """Return True if this contains no value."""
    ...

  def unwrap(self) -> T:
    """
    Extract the value, raising an exception if None.

    :returns: The wrapped value if Some
    :rtype: T
    :raises ValueError: If this is Nothing
    """
    ...

  def unwrap_or(self, default: T) -> T:
    """
    Extract the value or return a default if Nothing.

    :param default: Value to return if Nothing
    :type default: T
    :returns: The wrapped value if Some, otherwise default
    :rtype: T
    """
    ...

  def map(self, func: Callable[[T], U]) -> 'MaybeProtocol[U]':
    """
    Transform the Some value using the provided function.

    :param func: Function to apply to the Some value
    :type func: Callable[[T], U]
    :returns: Some with transformed value if this is Some, otherwise Nothing
    :rtype: MaybeProtocol[U]
    """
    ...

  def and_then(self, func: Callable[[T], 'MaybeProtocol[U]']) -> 'MaybeProtocol[U]':
    """
    Chain Maybe operations (monadic bind).

    :param func: Function that takes Some value and returns a Maybe
    :type func: Callable[[T], MaybeProtocol[U]]
    :returns: Result of applying func if this is Some, otherwise Nothing
    :rtype: MaybeProtocol[U]
    """
    ...
