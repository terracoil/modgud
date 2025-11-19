"""
Ok result type for successful computations.

This module provides the Ok class representing successful Result values,
following the single class per file principle.
"""

from typing import Any, Callable, TypeVar

from .result_base import Result

T = TypeVar('T')
U = TypeVar('U')
E = TypeVar('E')


class Ok(Result[T, E]):
  """
  Represents a successful result containing a value.
  """

  def __init__(self, value: T) -> None:
    """
    Initialize an Ok result.

    Args:
        value: The success value to wrap

    """
    self._value = value

  def is_ok(self) -> bool:
    """Return True since this is an Ok result."""
    return True

  def is_err(self) -> bool:
    """Return False since this is not an Err result."""
    return False

  def unwrap(self) -> T:
    """Extract the wrapped value."""
    return self._value

  def unwrap_or(self, default: T) -> T:
    """Return the wrapped value, ignoring the default."""
    return self._value

  def map(self, func: Callable[[T], U]) -> Result[U, E]:
    """Apply the function to the wrapped value."""
    return Ok(func(self._value))

  def and_then(self, func: Callable[[T], Result[U, E]]) -> Result[U, E]:
    """Apply the function to the wrapped value."""
    return func(self._value)

  def __eq__(self, other: Any) -> bool:
    """Check equality with another Result."""
    result = False
    if isinstance(other, Ok):
      result = self._value == other._value
    return result

  def __repr__(self) -> str:
    """Return string representation."""
    return f'Ok({self._value!r})'
