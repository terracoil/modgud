"""Unified guarded_expression decorator combining guards and implicit returns.

`guarded_expression` is the primary modgud decorator. It applies guard
clauses to a function and, by default, also performs the implicit-return
AST rewrite so the last expression in each branch is returned automatically.
Strict mode: if `implicit_return=True` and the AST rewrite refuses (source
unavailable, unsupported construct, etc.), the exception propagates from
the decoration site.
"""

from __future__ import annotations

from typing import Any, Callable

from idunn import Invert

from modgud.domain.guarded_expr import (
  GuardClauseError,
  GuardFailureEnum,
  GuardFunction,
  GuardPort,
)
from modgud.domain.implicit_ret import ImplicitReturnPort

from .method_descriptors import MethodDescriptors


class guarded_expression:
  """Guard a function and, by default, enable implicit returns.

  Guards return ``True`` (pass) or an error message string (fail).
  Failures are dispatched per ``strategy``; the payload paired with the
  strategy is ``on_failure``:

  - ``ERROR_RAISE`` (default): ``on_failure`` is the exception class to raise.
  - ``ERROR_RETURN``: same exception, returned instead of raised.
  - ``RETURN_VALUE``: ``on_failure`` returned as-is.
  - ``CALL_HANDLER``: ``on_failure(errors, *args, **kwargs)`` is called.

  ``continuance`` caps how many guards past the first failure are evaluated.
  ``runtime`` and ``transformer`` are injected by Idunn, which discovers modgud's adapters the
  first time a decoration leaves either one to it. Pass either explicitly to substitute a
  different implementation (e.g. a test fake); pass both and nothing is discovered at all.
  """

  runtime: GuardPort  # assigned by @Invert
  transformer: ImplicitReturnPort  # assigned by @Invert

  @Invert(bootstrap='modgud')
  def __init__(
    self,
    *guards: GuardFunction,
    implicit_return: bool = True,
    strategy: GuardFailureEnum = GuardFailureEnum.ERROR_RAISE,
    on_failure: Any = GuardClauseError,
    continuance: int = 0,
    runtime: GuardPort,
    transformer: ImplicitReturnPort,
  ) -> None:
    """Capture the guard configuration; ``runtime`` and ``transformer`` are injected by Idunn."""
    self._guards: tuple[GuardFunction, ...] = guards
    self._implicit_return: bool = implicit_return
    self._strategy: GuardFailureEnum = strategy
    self._on_failure: Any = on_failure
    self._continuance: int = continuance

  def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
    """Apply the (optional) implicit-return rewrite, then wrap ``func`` with guard dispatch.

    ``func`` may also be a ``staticmethod`` / ``classmethod`` object (modgud applied outside
    the built-in); the result is then a descriptor of the same kind.
    """
    plain, kind = MethodDescriptors.unwrap(func)
    already_transformed: bool = getattr(plain, '__implicit_return__', False)
    target: Callable[..., Any] = (
      self.transformer.transform_function(plain)
      if self._implicit_return and not already_transformed
      else plain
    )
    wrapped: Callable[..., Any] = self.runtime.wrap_function(
      target, self._guards, self._strategy, self._on_failure, self._continuance
    )
    # Lets @implicit_return() refuse to sit above this wrapper: its re-compile would drop the guards
    wrapped.__modgud_guarded__ = True  # type: ignore[attr-defined]
    if self._implicit_return:
      wrapped.__implicit_return__ = True  # type: ignore[attr-defined]
    return MethodDescriptors.rewrap(wrapped, kind)
