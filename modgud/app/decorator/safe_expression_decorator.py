"""Safe expression decorator for monadic error handling.

This module provides the SafeExpressionDecorator class that wraps function results
in Result types, following the single class per file principle.
"""

import functools
from dataclasses import dataclass
from typing import Any, Callable, TypeVar

from modgud.infrastructure import ErrResult, Ok

T = TypeVar('T')
R = TypeVar('R')


@dataclass(frozen=True)
class SafeExpressionDecorator:
  """Decorator that wraps function results in Result types for safe error handling.

  Functions decorated with this class automatically catch exceptions
  and return Ok[T, Exception] | ErrResult[T, Exception] instead of raising exceptions.
  """

  catch_exceptions: tuple[type[Exception], ...] = (Exception,)
  convert_none: bool = False

  def __call__(
    self, func: Callable[..., T]
  ) -> Callable[..., Ok[T, Exception] | ErrResult[T, Exception]]:
    """Decorate a function to return Result types.

    Args:
        func: Function to decorate

    Returns:
        Decorated function that returns Ok[T, Exception] | ErrResult[T, Exception]

    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Ok[T, Exception] | ErrResult[T, Exception]:
      """Execute function and wrap result in Result type."""
      result: Ok[T, Exception] | ErrResult[T, Exception]
      try:
        value = func(*args, **kwargs)

        # Convert None to Err if requested
        if self.convert_none and value is None:
          error: Exception = ValueError(f'Function {func.__name__} returned None')
          result = ErrResult(error)
        else:
          result = Ok(value)

      except self.catch_exceptions as e:
        result = ErrResult(e)

      return result

    # Preserve function metadata
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__annotations__ = func.__annotations__

    # Mark as safe expression
    wrapper.__safe_expression__ = True  # type: ignore[attr-defined]

    return wrapper
