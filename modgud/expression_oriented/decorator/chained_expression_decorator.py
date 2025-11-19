"""
Chained expression decorator for fluent interfaces.

This module provides the ChainedExpressionDecorator class that wraps function results
in ChainableExpression instances, following the single class per file principle.
"""

from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Any, Callable, TypeVar

if TYPE_CHECKING:
  from ..tool.chainable_expression import ChainableExpression

T = TypeVar('T')


class ChainedExpressionDecorator:
  """
  Decorator that wraps function results in ChainableExpression for method chaining.
  """

  def __init__(self, auto_unwrap: bool = False) -> None:
    """
    Initialize the chained expression decorator.

    Args:
        auto_unwrap: If True, automatically unwrap single ChainableExpression arguments

    """
    self.auto_unwrap = auto_unwrap

  def __call__(self, func: Callable[..., T]) -> Callable[..., 'ChainableExpression[T]']:
    """
    Decorate a function to return ChainableExpression.

    Args:
        func: Function to decorate

    Returns:
        Decorated function that returns ChainableExpression[T]

    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> 'ChainableExpression[T]':
      """Execute function and wrap result in ChainableExpression."""
      processed_args = args
      processed_kwargs = kwargs

      # Auto-unwrap ChainableExpression arguments if requested
      if self.auto_unwrap:
        from ..tool.chainable_expression import ChainableExpression

        unwrapped_args = []
        for arg in args:
          if isinstance(arg, ChainableExpression):
            unwrapped_args.append(arg.unwrap())
          else:
            unwrapped_args.append(arg)
        processed_args = tuple(unwrapped_args)

        unwrapped_kwargs = {}
        for key, value in kwargs.items():
          if isinstance(value, ChainableExpression):
            unwrapped_kwargs[key] = value.unwrap()
          else:
            unwrapped_kwargs[key] = value
        processed_kwargs = unwrapped_kwargs

      result = func(*processed_args, **processed_kwargs)
      from ..tool.chainable_expression import ChainableExpression

      return ChainableExpression(result)

    # Preserve function metadata
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__annotations__ = func.__annotations__

    # Mark as chained expression
    wrapper.__chained_expression__ = True

    return wrapper
