from __future__ import annotations

from typing import Any, Callable

from ..domain.protocols import SafeDecoratorFactoryProtocol
from ..domain.result_protocol import ResultProtocol
from .err_result import Err
from .ok_result import Ok


class SafeExpressionFactory(SafeDecoratorFactoryProtocol):
  """
  Factory for creating safe expression decorators and utilities.
  Provides error-safe functional programming patterns.
  """

  def create_decorator(
    self, catch_exceptions: tuple[type[Exception], ...] = (Exception,), convert_none: bool = False
  ) -> Callable[[Callable], Callable]:
    """
    Create a safe expression decorator function.

    Args:
        catch_exceptions: Tuple of exception types to catch
        convert_none: If True, convert None results to Err

    Returns:
        Callable: A decorator for creating safe functions

    """

    def safe_decorator(func: Callable) -> Callable:
      """
      Decorator that wraps function results in Result types (Ok/Err).

      Args:
          func: Function to decorate

      Returns:
          Decorated function that returns Result[T, Exception]

      """

      def wrapper(*args, **kwargs) -> ResultProtocol:
        try:
          result = func(*args, **kwargs)
          if convert_none and result is None:
            return Err('Function returned None')
          return Ok(result)
        except catch_exceptions as e:
          return Err(e)

      # Preserve function metadata
      wrapper.__name__ = func.__name__
      wrapper.__doc__ = func.__doc__
      wrapper.__annotations__ = func.__annotations__

      return wrapper

    return safe_decorator

  def create_result(self, value: Any, is_success: bool = True) -> ResultProtocol:
    """
    Create a Result instance (Ok or Err).

    Args:
        value: The value to wrap
        is_success: True for Ok, False for Err

    Returns:
        ResultProtocol: Ok or Err instance

    """
    return Ok(value) if is_success else Err(value)
