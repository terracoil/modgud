"""
Abstract base class for Result types.

This module provides the Result abstract base class following the single
class per file principle.
"""

from abc import ABC, abstractmethod
from typing import Callable, Generic, TypeVar

T = TypeVar('T')
U = TypeVar('U')
E = TypeVar('E')


class Result(ABC, Generic[T, E]):
  """
  Abstract base class for Result types.

  Result represents a value that can be either a success (Ok) or an error (Err).
  This enables safe error handling without exceptions.
  """

  @abstractmethod
  def is_ok(self) -> bool:
    """Return True if this is an Ok result."""
    pass

  @abstractmethod
  def is_err(self) -> bool:
    """Return True if this is an Err result."""
    pass

  @abstractmethod
  def unwrap(self) -> T:
    """
    Extract the Ok value, raising an exception if this is an Err.

    Returns:
        The wrapped value if Ok

    Raises:
        ValueError: If this is an Err result

    """
    pass

  @abstractmethod
  def unwrap_or(self, default: T) -> T:
    """
    Extract the Ok value or return a default if this is an Err.

    Args:
        default: Value to return if this is an Err

    Returns:
        The wrapped value if Ok, otherwise default

    """
    pass

  @abstractmethod
  def map(self, func: Callable[[T], U]) -> 'Result[U, E]':
    """
    Transform the Ok value using the provided function.

    Args:
        func: Function to apply to the Ok value

    Returns:
        Ok with transformed value if this is Ok, otherwise unchanged Err

    """
    pass

  @abstractmethod
  def and_then(self, func: Callable[[T], 'Result[U, E]']) -> 'Result[U, E]':
    """
    Chain Result operations (monadic bind).

    Args:
        func: Function that takes Ok value and returns a Result

    Returns:
        Result of applying func if this is Ok, otherwise unchanged Err

    """
    pass
