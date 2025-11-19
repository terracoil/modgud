"""
Standalone implicit_return decorator.

Provides a decorator that enables Ruby-style implicit returns where the last
expression in each code path is automatically returned without explicit return
statements.

This decorator can be used independently or composed with other decorators
like @guarded_expression.
"""

import functools
import inspect
from textwrap import dedent
from typing import Any, Callable, TypeVar, cast

from ..core.errors import UnsupportedConstructError
from ..core.implicit_return import ImplicitReturnTransformer

# Type variable for generic function signatures
F = TypeVar('F', bound=Callable[..., Any])


class implicit_return:
  """
  Decorator that enables implicit returns for functions.

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
      MissingImplicitReturnError: If a code path doesn't yield a value
      UnsupportedConstructError: If unsupported constructs are found at tail position

  """

  def __call__(self, func: F) -> F:
    """
    Transform the function to use implicit returns.

    Args:
        func: The function to transform

    Returns:
        The transformed function with implicit return semantics

    """
    # Extract and parse source
    try:
      source = dedent(inspect.getsource(func))
    except OSError as e:
      raise UnsupportedConstructError(
        f'Source unavailable — @implicit_return requires importable source code for function {func.__name__}.'
      ) from e

    # Transform the AST
    new_tree, filename = ImplicitReturnTransformer.apply_implicit_return_transform(
      source, func.__name__
    )

    # Execute in copy of original scope - preserves imports/closures
    env = func.__globals__.copy()
    code = compile(new_tree, filename=filename, mode='exec')
    exec(code, env)

    transformed = env[func.__name__]  # Extract the redefined function

    # Wrap to preserve metadata
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
      return transformed(*args, **kwargs)

    # Preserve signature for IDE autocomplete and runtime introspection
    wrapper.__signature__ = inspect.signature(func)  # type: ignore[attr-defined]
    wrapper.__annotations__ = getattr(func, '__annotations__', {})

    # Mark as transformed for debugging/introspection
    wrapper.__implicit_return__ = True  # type: ignore[attr-defined]

    return cast(F, wrapper)


# Convenience: Allow using @implicit_return without parentheses
implicit_return = implicit_return()
