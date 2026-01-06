"""Port definition for factories that create safe expression decorators."""

from __future__ import annotations

from typing import Any, Callable, Protocol, runtime_checkable

from ..result_port import ResultPort


@runtime_checkable
class SafeDecoratorFactoryPort(Protocol):
  """Interface for factories that create safe expression decorators."""

  def create_decorator(
    self, catch_exceptions: tuple[type[Exception], ...] = (Exception,), convert_none: bool = False
  ) -> Callable[[Callable], Callable]:
    """
    Create a decorator that wraps function results in Result types.

    Args:
        catch_exceptions: Tuple of exception types to catch
        convert_none: If True, convert None results to Err

    Returns:
        Callable: A decorator function that returns Result[T, Exception]

    """
    ...

  def create_result(self, value: Any, is_success: bool = True) -> ResultPort:
    """
    Create a Result instance.

    Args:
        value: The name to wrap
        is_success: True for Ok, False for Err

    Returns:
        Result instance

    """
    ...
