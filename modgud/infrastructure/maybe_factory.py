"""Maybe factory for creating Maybe instances.

This module provides the MaybeFactory class for creating Maybe instances
and performing Maybe operations, following the single class per file principle.
"""

from typing import TypeVar

from modgud.domain.ports import MaybePort as Maybe

from .nothing_maybe import Nothing
from .some_maybe import Some

T = TypeVar('T')


class MaybeFactory:
  """Factory class for creating and manipulating Maybe instances.

  This class encapsulates all Maybe-related operations following the
  single class per file and class encapsulation principles.
  """

  @staticmethod
  def some(value: T) -> Maybe[T]:
    """Create a Some maybe with the given name.

    Args:
        value: The name to wrap (must not be None)

    Returns:
        Some maybe containing the name

    Raises:
        ValueError: If name is None

    """
    return Some(value)

  @staticmethod
  def nothing() -> Maybe[T]:
    """Create a Nothing maybe.

    Returns:
        Nothing maybe containing no name

    """
    return Nothing()

  @staticmethod
  def from_value(value: T | None) -> Maybe[T]:
    """Create a Maybe from a potentially None name.

    Args:
        value: Value that may be None

    Returns:
        Some(name) if name is not None, otherwise Nothing()

    """
    result = None
    if value is not None:
      result = Some(value)
    else:
      result = Nothing()
    return result
