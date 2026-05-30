"""Standalone implicit_return decorator.

Ruby-style implicit returns: the last expression in each branch is the
function's return value. Explicit `return` statements are not allowed.
"""

from typing import Any, Callable, TypeVar, cast

from modgud.infrastructure import ImplicitReturnTransformer

F = TypeVar('F', bound=Callable[..., Any])


def implicit_return(func: F) -> F:
  """Transform `func` to use implicit returns.

  :raises ExplicitReturnDisallowedError: if explicit return statements are found.
  :raises MissingImplicitReturnError: if a code path doesn't yield a value.
  :raises UnsupportedConstructError: if an unsupported construct is at tail position.
  :raises ValueError: if the function source cannot be extracted.
  """
  transformed = ImplicitReturnTransformer.transform_function(func)
  transformed.__implicit_return__ = True  # type: ignore[attr-defined]
  return cast(F, transformed)
