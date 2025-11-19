"""
Some maybe type for values that exist.

This module provides the Some class representing Maybe values that contain data,
following the single class per file principle.
"""

from typing import Any, Callable, TypeVar

from .maybe_base import Maybe

T = TypeVar('T')
U = TypeVar('U')


class Some(Maybe[T]):
  """
  Represents a Maybe that contains a value.
  """

  def __init__(self, value: T) -> None:
    """
    Initialize a Some value.

    Args:
        value: The value to wrap (should not be None)

    Raises:
        ValueError: If value is None

    """
    if value is None:
      raise ValueError('Some cannot contain None value, use Nothing instead')
    self._value = value

  def is_some(self) -> bool:
    """Return True since this contains a value."""
    return True

  def is_nothing(self) -> bool:
    """Return False since this contains a value."""
    return False

  def unwrap(self) -> T:
    """Extract the wrapped value."""
    return self._value

  def unwrap_or(self, default: T) -> T:
    """Return the wrapped value, ignoring the default."""
    return self._value

  def map(self, func: Callable[[T], U]) -> Maybe[U]:
    """Apply the function to the wrapped value."""
    return Some(func(self._value))

  def and_then(self, func: Callable[[T], Maybe[U]]) -> Maybe[U]:
    """Apply the function to the wrapped value."""
    return func(self._value)

  def __eq__(self, other: Any) -> bool:
    """Check equality with another Maybe."""
    result = False
    if isinstance(other, Some):
      result = self._value == other._value
    return result

  def __repr__(self) -> str:
    """Return string representation."""
    return f'Some({self._value!r})'
