"""
Chainable expression wrapper for fluent interfaces.

This module provides the ChainableExpression class that enables method
chaining for any object, following the single class per file principle.
"""

from typing import Any, Callable, Generic, TypeVar

T = TypeVar('T')
R = TypeVar('R')


class ChainableExpression(Generic[T]):
  """
  Wrapper that enables method chaining for any object.

  This class wraps values and provides chainable methods for functional-style
  data transformation and fluent interfaces.
  """

  def __init__(self, value: T) -> None:
    """
    Initialize a chainable expression.

    Args:
        value: The value to wrap for chaining

    """
    self._value = value

  def map(self, func: Callable[[T], R]) -> 'ChainableExpression[R]':
    """
    Transform the wrapped value using the provided function.

    Args:
        func: Function to apply to the wrapped value

    Returns:
        ChainableExpression wrapping the transformed value

    """
    return ChainableExpression(func(self._value))

  def filter(self, predicate: Callable[[T], bool]) -> 'ChainableExpression[T | None]':
    """
    Filter the wrapped value using a predicate.

    Args:
        predicate: Function that returns True to keep the value

    Returns:
        ChainableExpression with the value if predicate passes, otherwise None

    """
    result = None
    if predicate(self._value):
      result = self._value
    return ChainableExpression(result)

  def tap(self, func: Callable[[T], Any]) -> 'ChainableExpression[T]':
    """
    Execute a side effect function without changing the wrapped value.

    Args:
        func: Function to execute for side effects

    Returns:
        ChainableExpression with the unchanged value

    """
    func(self._value)
    return self

  def unwrap(self) -> T:
    """
    Extract the wrapped value.

    Returns:
        The wrapped value

    """
    return self._value

  def unwrap_or(self, default: T) -> T:
    """
    Extract the wrapped value or return default if None.

    Args:
        default: Value to return if wrapped value is None

    Returns:
        The wrapped value or default

    """
    result = default
    if self._value is not None:
      result = self._value
    return result

  def __repr__(self) -> str:
    """Return string representation."""
    return f'ChainableExpression({self._value!r})'

  def __eq__(self, other: Any) -> bool:
    """Check equality with another ChainableExpression."""
    result = False
    if isinstance(other, ChainableExpression):
      result = self._value == other._value
    else:
      result = self._value == other
    return result
