"""Factory for creating safe expression decorators."""

from __future__ import annotations

from typing import Any, Callable

from modgud.domain.ports import ResultPort, SafeDecoratorFactoryPort

from .err_result import ErrResult
from .ok_result import Ok


class SafeExpressionFactory(SafeDecoratorFactoryPort):
  """Factory for creating safe expression decorators and utilities.

  Provides error-safe functional programming patterns.
  """

  def create_decorator(
    self, catch_exceptions: tuple[type[Exception], ...] = (Exception,), convert_none: bool = False
  ) -> Callable[[Callable], Callable]:
    """Create a safe expression decorator function.

    Args:
        catch_exceptions: Tuple of exception types to catch
        convert_none: If True, convert None results to Err

    Returns:
        Callable: A decorator for creating safe functions

    """

    def safe_decorator(func: Callable) -> Callable:
      """Wrap function results in Result types (Ok/Err).

      Args:
          func: Function to decorate

      Returns:
          Decorated function that returns Result[T, Exception]

      """

      def wrapper(*args, **kwargs) -> ResultPort:
        try:
          result = func(*args, **kwargs)
          if convert_none and result is None:
            return ErrResult('Function returned None')
          return Ok(result)
        except catch_exceptions as e:
          return ErrResult(e)

      # Preserve function metadata
      wrapper.__name__ = func.__name__
      wrapper.__doc__ = func.__doc__
      wrapper.__annotations__ = func.__annotations__

      return wrapper

    return safe_decorator

  def create_result(self, value: Any, is_success: bool = True) -> ResultPort:
    """Create a Result instance (Ok or Err).

    Args:
        value: The name to wrap
        is_success: True for Ok, False for Err

    Returns:
        ResultPort: Ok or Err instance

    """
    return Ok(value) if is_success else ErrResult(value)
