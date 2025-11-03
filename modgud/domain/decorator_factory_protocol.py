"""
Decorator factory protocols for the modgud domain layer.

This module defines the interfaces that decorator factories must implement,
allowing the app layer to depend on abstractions rather than concrete implementations.
"""

from __future__ import annotations

from typing import Any, Callable, Protocol, runtime_checkable

from .result_protocol import ResultProtocol


@runtime_checkable
class ChainableDecoratorFactoryProtocol(Protocol):
  """Interface for factories that create chainable expression decorators."""

  def create_decorator(self) -> Callable[[Callable], Callable]:
    """
    Create a decorator that makes functions return chainable expressions.

    Returns:
        Callable: A decorator function

    """
    ...

  def create_expression(self, value: Any) -> Any:
    """
    Wrap a value for chaining.

    Args:
        value: The value to wrap

    Returns:
        Wrapped value with chaining capabilities

    """
    ...


@runtime_checkable
class SafeDecoratorFactoryProtocol(Protocol):
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

  def create_result(self, value: Any, is_success: bool = True) -> ResultProtocol:
    """
    Create a Result instance.

    Args:
        value: The value to wrap
        is_success: True for Ok, False for Err

    Returns:
        Result instance

    """
    ...
