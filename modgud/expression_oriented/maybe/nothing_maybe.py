"""
Nothing maybe type for absent values.

This module provides the Nothing class representing Maybe values that contain no data,
following the single class per file principle.
"""

from typing import Any, Callable, TypeVar

from ...domain.maybe_protocol import MaybeProtocol

T = TypeVar('T')
U = TypeVar('U')


class Nothing(MaybeProtocol[T]):
  """
  Represents a Maybe that contains no value.
  """

  def __init__(self) -> None:
    """Initialize a Nothing value."""
    pass

  def is_some(self) -> bool:
    """Return False since this contains no value."""
    return False

  def is_nothing(self) -> bool:
    """Return True since this contains no value."""
    return True

  def unwrap(self) -> T:
    """Raise an exception since there is no value."""
    raise ValueError('Called unwrap on Nothing')

  def unwrap_or(self, default: T) -> T:
    """Return the default value since there is no wrapped value."""
    return default

  def map(self, func: Callable[[T], U]) -> MaybeProtocol[U]:
    """Return Nothing unchanged."""
    return Nothing()

  def and_then(self, func: Callable[[T], MaybeProtocol[U]]) -> MaybeProtocol[U]:
    """Return Nothing unchanged."""
    return Nothing()

  def __eq__(self, other: Any) -> bool:
    """Check equality with another Maybe."""
    return isinstance(other, Nothing)

  def __repr__(self) -> str:
    """Return string representation."""
    return 'Nothing()'
