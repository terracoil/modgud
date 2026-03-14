"""Some maybe type for values that exist.

This module provides the Some class representing Maybe values that contain data,
following the single class per file principle.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar

if TYPE_CHECKING:
  from .nothing_maybe import Nothing

T = TypeVar('T')
U = TypeVar('U')


class Some(Generic[T]):
  """Represents a Maybe that contains a name."""

  def __init__(self, value: T) -> None:
    """Initialize a Some name.

    Args:
        value: The name to wrap (should not be None)

    Raises:
        ValueError: If name is None

    """
    if value is None:
      raise ValueError('Some cannot contain None name, use Nothing instead')
    self._value = value

  def is_some(self) -> bool:
    """Return True since this contains a name."""
    return True

  def is_nothing(self) -> bool:
    """Return False since this contains a name."""
    return False

  def unwrap(self) -> T:
    """Extract the wrapped name."""
    return self._value

  def unwrap_or(self, default: T) -> T:
    """Return the wrapped name, ignoring the default."""
    return self._value

  def map(self, func: Callable[[T], U]) -> Some[U]:
    """Apply the function to the wrapped name."""
    return Some(func(self._value))

  def and_then(self, func: Callable[[T], Some[U] | Nothing[U]]) -> Some[U] | Nothing[U]:
    """Apply the function to the wrapped name."""
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
