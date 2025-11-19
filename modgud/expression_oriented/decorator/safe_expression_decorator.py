"""
Safe expression decorator for monadic error handling.

This module provides the SafeExpressionDecorator class that wraps function results
in Result types, following the single class per file principle.
"""

import functools
from typing import Any, Callable, TypeVar

from ..results.err_result import Err
from ..results.ok_result import Ok
from ...domain.result_protocol import ResultProtocol as Result

T = TypeVar('T')
R = TypeVar('R')


class SafeExpressionDecorator:
  """
  Decorator that wraps function results in Result types for safe error handling.

  Functions decorated with this class automatically catch exceptions
  and return Result[T, Exception] instead of raising exceptions.
  """

  def __init__(
    self, catch_exceptions: tuple[type[Exception], ...] = (Exception,), convert_none: bool = False
  ) -> None:
    """
    Initialize the safe expression decorator.

    Args:
        catch_exceptions: Tuple of exception types to catch (default: all exceptions)
        convert_none: If True, convert None results to Err (default: False)

    """
    self.catch_exceptions = catch_exceptions
    self.convert_none = convert_none

  def __call__(self, func: Callable[..., T]) -> Callable[..., Result[T, Exception]]:
    """
    Decorate a function to return Result types.

    Args:
        func: Function to decorate

    Returns:
        Decorated function that returns Result[T, Exception]

    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Result[T, Exception]:
      """Execute function and wrap result in Result type."""
      result = None
      try:
        value = func(*args, **kwargs)

        # Convert None to Err if requested
        if self.convert_none and value is None:
          error = ValueError(f'Function {func.__name__} returned None')
          result = Err(error)
        else:
          result = Ok(value)

      except self.catch_exceptions as e:
        result = Err(e)

      return result

    # Preserve function metadata
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__annotations__ = func.__annotations__

    # Mark as safe expression
    wrapper.__safe_expression__ = True

    return wrapper
