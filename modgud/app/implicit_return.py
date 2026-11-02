"""Standalone implicit_return decorator.

Ruby-style implicit returns: the last expression in each branch is the
function's return value. Explicit `return` statements are not allowed.
Apply it with parentheses: ``@implicit_return()``.
"""

from __future__ import annotations

from typing import Any, Callable, TypeVar, cast

from idunn import Invert

from modgud.domain.implicit_ret.ports import ImplicitReturnTransformerPort

from .method_descriptors import MethodDescriptors
from .wiring import Wiring

F = TypeVar('F', bound=Callable[..., Any])


class implicit_return:
  """Transform a function to use implicit returns.

  ``transformer`` is injected by Idunn; pass it explicitly to substitute a
  different implementation (e.g. a test fake).

  :raises ExplicitReturnDisallowedError: if explicit return statements are found.
  :raises MissingImplicitReturnError: if a code path doesn't yield a value.
  :raises UnsupportedConstructError: if an unsupported construct is at tail position.
  :raises ValueError: if the function source cannot be extracted.
  :raises TypeError: if applied above ``@guarded_expression``, whose guards the rewrite would drop.
  """

  transformer: ImplicitReturnTransformerPort  # assigned by @Invert

  def __new__(cls, **options: Any) -> implicit_return:
    """Discover modgud's adapters on first use (a cached no-op afterwards), then build."""
    Wiring.ensure()
    return super().__new__(cls)

  @Invert()
  def __init__(self, *, transformer: ImplicitReturnTransformerPort) -> None:
    """Receive the transformer port from Idunn (or from the caller)."""

  def __call__(self, func: F) -> F:
    """Rewrite ``func`` so the last expression in each branch is returned.

    ``func`` may also be a ``staticmethod`` / ``classmethod`` object; the result is then a
    descriptor of the same kind.

    :raises TypeError: if ``func`` is already a ``guarded_expression`` wrapper. The rewrite
      re-reads the original source, so the guards would silently disappear.
    """
    plain, kind = MethodDescriptors.unwrap(func)
    if getattr(plain, '__modgud_guarded__', False):
      raise TypeError(
        '@implicit_return() must sit below @guarded_expression; put it closer to the def, '
        'or pass implicit_return=True'
      )
    transformed: Callable[..., Any] = self.transformer.transform_function(plain)
    transformed.__implicit_return__ = True  # type: ignore[attr-defined]
    return cast(F, MethodDescriptors.rewrap(transformed, kind))
