"""
Abstract base class for Maybe types.

This module provides the Maybe abstract base class following the single
class per file principle.
"""

from abc import ABC, abstractmethod
from typing import Callable, Generic, TypeVar

T = TypeVar('T')
U = TypeVar('U')


class Maybe(ABC, Generic[T]):
  """
  Abstract base class for Maybe types.

  Maybe represents a value that may or may not exist, providing safe operations
  for working with optional values without null pointer exceptions.
  """

  @abstractmethod
  def is_some(self) -> bool:
    """Return True if this contains a value."""
    pass

  @abstractmethod
  def is_nothing(self) -> bool:
    """Return True if this contains no value."""
    pass

  @abstractmethod
  def unwrap(self) -> T:
    """
    Extract the value, raising an exception if None.

    Returns:
        The wrapped value if Some

    Raises:
        ValueError: If this is Nothing

    """
    pass

  @abstractmethod
  def unwrap_or(self, default: T) -> T:
    """
    Extract the value or return a default if Nothing.

    Args:
        default: Value to return if Nothing

    Returns:
        The wrapped value if Some, otherwise default

    """
    pass

  @abstractmethod
  def map(self, func: Callable[[T], U]) -> 'Maybe[U]':
    """
    Transform the Some value using the provided function.

    Args:
        func: Function to apply to the Some value

    Returns:
        Some with transformed value if this is Some, otherwise Nothing

    """
    pass

  @abstractmethod
  def and_then(self, func: Callable[[T], 'Maybe[U]']) -> 'Maybe[U]':
    """
    Chain Maybe operations (monadic bind).

    Args:
        func: Function that takes Some value and returns a Maybe

    Returns:
        Result of applying func if this is Some, otherwise Nothing

    """
    pass
