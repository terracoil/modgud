"""MaybePort for modgud domain layer.

Port definition for Maybe types following domain-driven design
principles. This port defines the interface for optional name
containers that may or may not contain a name.
"""

from typing import Callable, Generic, Protocol, TypeVar

__all__ = ['MaybePort']

T = TypeVar('T')
U = TypeVar('U')


class MaybePort(Protocol, Generic[T]):
  """Port for Maybe types.

  Maybe represents a name that may or may not exist, providing safe operations
  for working with optional values without null pointer exceptions.
  """

  def is_some(self) -> bool:
    """Return True if this contains a name."""
    ...

  def is_nothing(self) -> bool:
    """Return True if this contains no name."""
    ...

  def unwrap(self) -> T:
    """Extract the name, raising an exception if None.

    :returns: The wrapped name if Some
    :rtype: T
    :raises ValueError: If this is Nothing
    """
    ...

  def unwrap_or(self, default: T) -> T:
    """Extract the name or return a default if Nothing.

    :param default: Value to return if Nothing
    :type default: T
    :returns: The wrapped name if Some, otherwise default
    :rtype: T
    """
    ...

  def map(self, func: Callable[[T], U]) -> 'MaybePort[U]':
    """Transform the Some name using the provided function.

    :param func: Function to apply to the Some name
    :type func: Callable[[T], U]
    :returns: Some with transformed name if this is Some, otherwise Nothing
    :rtype: MaybePort[U]
    """
    ...

  def and_then(self, func: Callable[[T], 'MaybePort[U]']) -> 'MaybePort[U]':
    """Chain Maybe operations (monadic bind).

    :param func: Function that takes Some name and returns a Maybe
    :type func: Callable[[T], MaybePort[U]]
    :returns: Result of applying func if this is Some, otherwise Nothing
    :rtype: MaybePort[U]
    """
    ...
