"""
Chained expression factory for creating chained expression decorators.

This module provides the ChainedExpressionFactory class for creating chained expression decorators,
following the single class per file principle.
"""

from __future__ import annotations

from typing import Callable, TypeVar, Union

from ...app.decorator.chained_expression_decorator import ChainedExpressionDecorator
from ..tool.chainable_expression import ChainableExpression

T = TypeVar('T')


class ChainedExpressionFactory:
  """
  Factory class for creating chained expression decorators.

  This class encapsulates the creation of chained expression decorators
  following the single class per file and class encapsulation principles.
  """

  @staticmethod
  def create_decorator(auto_unwrap: bool = False) -> ChainedExpressionDecorator:
    """
    Create a chained expression decorator with specified options.

    Args:
        auto_unwrap: If True, automatically unwrap ChainableExpression arguments

    Returns:
        ChainedExpressionDecorator instance

    """
    return ChainedExpressionDecorator(auto_unwrap=auto_unwrap)

  @staticmethod
  def chained_expression(
    func: Callable[..., T] | None = None, *, auto_unwrap: bool = False
  ) -> Union[Callable[..., ChainableExpression[T]], ChainedExpressionDecorator]:
    """
    Create a chained expression decorator that can be used with or without parameters.

    This method provides the convenient @chained_expression decorator interface
    while maintaining proper class encapsulation.

    Examples:
        @ChainedExpressionFactory.chained_expression
        def add(x, y):
            return x + y

        @ChainedExpressionFactory.chained_expression(auto_unwrap=True)
        def multiply(x, y):
            return x * y

    Args:
        func: Function to decorate (when used without parameters)
        auto_unwrap: If True, automatically unwrap ChainableExpression arguments

    Returns:
        Decorated function or decorator instance

    """
    result = None
    if func is None:
      # Called with parameters: @chained_expression(...)
      result = ChainedExpressionDecorator(auto_unwrap=auto_unwrap)
    else:
      # Called without parameters: @chained_expression
      decorator = ChainedExpressionDecorator()
      result = decorator(func)
    return result

  @staticmethod
  def chain(value: T) -> ChainableExpression[T]:
    """
    Wrap a value in a ChainableExpression for method chaining.

    Args:
        value: Value to wrap

    Returns:
        ChainableExpression wrapping the value

    """
    return ChainableExpression(value)
