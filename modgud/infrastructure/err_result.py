"""
ErrResult result type for failed computations.

This module provides the ErrResult class representing failed Result values,
following the single class per file principle.
"""

from typing import Any, Callable, TypeVar

from ..domain.ports.result_port import ResultPort

T = TypeVar('T')
U = TypeVar('U')
E = TypeVar('E')


class ErrResult(ResultPort[T, E]):
  """Represents a failed result containing an error value."""

  def __init__(self, error: E) -> None:
    """
    Initialize an ErrResult result.

    Args:
        error: The error value to wrap

    """
    self._error = error

  def is_ok(self) -> bool:
    """Return False since this is not an Ok result."""
    return False

  def is_err(self) -> bool:
    """Return True since this is an ErrResult result."""
    return True

  def unwrap(self) -> T:
    """Raise an exception since this is an error."""
    raise ValueError(f'Called unwrap on ErrResult: {self._error!r}')

  def unwrap_or(self, default: T) -> T:
    """Return the default value since this is an error."""
    return default

  def map(self, func: Callable[[T], U]) -> ResultPort[U, E]:
    """Return self unchanged since this is an error."""
    return ErrResult(self._error)

  def and_then(self, func: Callable[[T], ResultPort[U, E]]) -> ResultPort[U, E]:
    """Return self unchanged since this is an error."""
    return ErrResult(self._error)

  def __eq__(self, other: Any) -> bool:
    """Check equality with another Result."""
    result = False
    if isinstance(other, ErrResult):
      result = self._error == other._error
    return result

  def __repr__(self) -> str:
    """Return string representation."""
    return f'ErrResult({self._error!r})'
