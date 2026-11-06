"""Standalone implicit_return decorator.

Ruby-style implicit returns: the last expression in each branch is the
function's return value. Explicit `return` statements are not allowed.
Apply it with parentheses: ``@implicit_return()``.
"""

from __future__ import annotations

from idunn import Invert

from modgud.domain.ports import ImplicitReturnPort
from modgud.domain.types import F


class implicit_return:
  """Transform a function to use implicit returns.

  ``imp_return_port`` is injected by Idunn, which discovers modgud's adapters the first time a
  decoration leaves it to injection. Pass it explicitly to substitute a different
  implementation (e.g. a test fake), and nothing is discovered.

  :raises ExplicitReturnDisallowedError: if explicit return statements are found.
  :raises MissingImplicitReturnError: if a code path doesn't yield a value.
  :raises UnsupportedConstructError: if an unsupported construct is at tail position.
  :raises ValueError: if the function source cannot be extracted.
  :raises TypeError: if applied above ``@guarded_expression``, whose guards the rewrite would drop.
  """

  imp_return_port: ImplicitReturnPort  # assigned by @Invert

  # @Invert assigns the port parameters to self before the body runs.
  # noinspection PyUnusedLocal
  @Invert(bootstrap='modgud')
  def __init__(self, *, imp_return_port: ImplicitReturnPort) -> None:
    """Receive the implicit-return port from Idunn (or from the caller)."""

  def __call__(self, func: F) -> F:
    """Transform :func: so the last expression in each branch is returned."""
    return self.imp_return_port.transform(func)
