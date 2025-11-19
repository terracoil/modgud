"""
Err result type for failed computations.

This module provides the Err class representing failed Result values,
following the single class per file principle.
"""

from typing import Any, Callable, TypeVar

from ...domain.result_protocol import ResultProtocol

T = TypeVar('T')
U = TypeVar('U')
E = TypeVar('E')


class Err(ResultProtocol[T, E]):
  """
  Represents a failed result containing an error value.
  """

  def __init__(self, error: E) -> None:
    """
    Initialize an Err result.

    Args:
        error: The error value to wrap

    """
    self._error = error

  def is_ok(self) -> bool:
    """Return False since this is not an Ok result."""
    return False

  def is_err(self) -> bool:
    """Return True since this is an Err result."""
    return True

  def unwrap(self) -> T:
    """Raise an exception since this is an error."""
    raise ValueError(f'Called unwrap on Err: {self._error!r}')

  def unwrap_or(self, default: T) -> T:
    """Return the default value since this is an error."""
    return default

  def map(self, func: Callable[[T], U]) -> ResultProtocol[U, E]:
    """Return self unchanged since this is an error."""
    return Err(self._error)

  def and_then(self, func: Callable[[T], ResultProtocol[U, E]]) -> ResultProtocol[U, E]:
    """Return self unchanged since this is an error."""
    return Err(self._error)

  def __eq__(self, other: Any) -> bool:
    """Check equality with another Result."""
    result = False
    if isinstance(other, Err):
      result = self._error == other._error
    return result

  def __repr__(self) -> str:
    """Return string representation."""
    return f'Err({self._error!r})'
