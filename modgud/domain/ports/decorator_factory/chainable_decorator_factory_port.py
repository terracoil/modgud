"""Port definition for factories that create chainable expression decorators."""

from __future__ import annotations

from typing import Any, Callable, Protocol, runtime_checkable


@runtime_checkable
class ChainableDecoratorFactoryPort(Protocol):
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
