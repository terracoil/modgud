from __future__ import annotations

from typing import Any, Callable

from ..domain.protocols import ChainableDecoratorFactoryProtocol
from .chainable_expression import ChainableExpression


class ChainedExpressionFactory(ChainableDecoratorFactoryProtocol):
  """
  Factory for creating chained expression decorators and utilities.
  Provides a clean interface for functional programming patterns.
  """

  def create_decorator(self) -> Callable[[Callable], Callable]:
    """
    Create a new chained expression decorator function.

    Returns:
        Callable: A decorator for creating chainable functions

    """

    def pipeable_decorator(func: Callable) -> Callable:
      """
      Decorator that makes a function return ChainableExpression for piping.

      Args:
          func: Function to decorate

      Returns:
          Decorated function that returns ChainableExpression

      """

      def wrapper(*args, **kwargs) -> ChainableExpression:
        result = func(*args, **kwargs)
        return ChainableExpression(result)

      # Preserve function metadata
      wrapper.__name__ = func.__name__
      wrapper.__doc__ = func.__doc__
      wrapper.__annotations__ = func.__annotations__

      return wrapper

    return pipeable_decorator

  def create_expression(self, value: Any) -> ChainableExpression:
    """
    Wrap a value in a ChainableExpression for method chaining.

    Args:
        value: The value to wrap

    Returns:
        ChainableExpression: Wrapped value with chaining capabilities

    """
    return ChainableExpression(value)

  def pipe(self, value: Any, *operations: Callable[[Any], Any]) -> Any:
    """
    Apply a series of operations to a value in sequence.

    Args:
        value: Initial value to transform
        *operations: Functions to apply in sequence

    Returns:
        Final transformed value

    """
    result = value
    for operation in operations:
      result = operation(result)
    return result
