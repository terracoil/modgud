"""Nothing maybe type for absent values.

This module provides the Nothing class representing Maybe values that contain no data,
following the single class per file principle.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar

if TYPE_CHECKING:
  from .some_maybe import Some

T = TypeVar('T')
U = TypeVar('U')


class Nothing(Generic[T]):
  """Represents a Maybe that contains no name."""

  def __init__(self) -> None:
    """Initialize a Nothing name."""
    pass

  def is_some(self) -> bool:
    """Return False since this contains no name."""
    return False

  def is_nothing(self) -> bool:
    """Return True since this contains no name."""
    return True

  def unwrap(self) -> T:
    """Raise an exception since there is no name."""
    raise ValueError('Called unwrap on Nothing')

  def unwrap_or(self, default: T) -> T:
    """Return the default name since there is no wrapped name."""
    return default

  def map(self, func: Callable[[T], U]) -> Nothing[U]:
    """Return Nothing unchanged."""
    return Nothing()

  def and_then(self, func: Callable[[T], Some[U] | Nothing[U]]) -> Nothing[U]:
    """Return Nothing unchanged."""
    return Nothing()

  def __eq__(self, other: Any) -> bool:
    """Check equality with another Maybe."""
    return isinstance(other, Nothing)

  def __repr__(self) -> str:
    """Return string representation."""
    return 'Nothing()'
