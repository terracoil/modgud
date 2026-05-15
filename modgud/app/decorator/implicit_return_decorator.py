"""Standalone implicit_return decorator.

Provides a decorator that enables Ruby-style implicit returns where the last
expression in each code path is automatically returned without explicit return
statements.

This decorator can be used independently or composed with other decorators
like @guarded_expression.
"""

from typing import Any, Callable, TypeVar, cast

from modgud.domain import UnsupportedConstructError
from modgud.infrastructure.transform import ImplicitReturnTransformer

# Type variable for generic function signatures
F = TypeVar('F', bound=Callable[..., Any])


class _ImplicitReturnDecorator:
  """Decorator that enables implicit returns for functions.

  Transforms a function to automatically return the last expression in each
  code path, similar to Ruby's implicit return behavior. Explicit return
  statements are not allowed when using this decorator.

  Usage:
      @implicit_return
      def calculate(x, y):
          if x > y:
              x * 2  # Implicitly returned
          else:
              y * 2  # Implicitly returned

      # Is equivalent to:
      def calculate(x, y):
          if x > y:
              return x * 2
          else:
              return y * 2

  Composition with other decorators:
      @implicit_return
      @guarded_expression(positive("x"))
      def process(x):
          result = x * 2
          result  # Implicitly returned

  Raises:
      ExplicitReturnDisallowedError: If explicit return statements are found
      MissingImplicitReturnError: If a code path doesn't yield a name
      UnsupportedConstructError: If unsupported constructs are found at tail position

  """

  def __call__(self, func: F) -> F:
    """Transform the function to use implicit returns.

    Args:
        func: The function to transform

    Returns:
        The transformed function with implicit return semantics

    """
    try:
      transformed = ImplicitReturnTransformer.transform_function(func)
    except ValueError as e:
      raise UnsupportedConstructError(str(e)) from e
    transformed.__implicit_return__ = True  # type: ignore[attr-defined]
    return cast(F, transformed)


implicit_return: _ImplicitReturnDecorator = _ImplicitReturnDecorator()
