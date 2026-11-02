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

from modgud.domain.guarded_expr import GuardClauseError, GuardFailureEnum, GuardFunction
from modgud.domain.guarded_expr.ports import GuardRuntimePort
from modgud.domain.implicit_ret.ports import ImplicitReturnTransformerPort

from .wiring import Wiring


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
  ``runtime`` and ``transformer`` are injected by Idunn; pass either explicitly to
  substitute a different implementation (e.g. a test fake).
  """

  runtime: GuardRuntimePort  # assigned by @Invert
  transformer: ImplicitReturnTransformerPort  # assigned by @Invert

  def __new__(cls, *guards: GuardFunction, **options: Any) -> guarded_expression:
    """Discover modgud's adapters on first use (a cached no-op afterwards), then build."""
    Wiring.ensure()
    return super().__new__(cls)

  @Invert()
  def __init__(
    self,
    *guards: GuardFunction,
    implicit_return: bool = True,
    strategy: GuardFailureEnum = GuardFailureEnum.ERROR_RAISE,
    on_failure: Any = GuardClauseError,
    continuance: int = 0,
    runtime: GuardRuntimePort,
    transformer: ImplicitReturnTransformerPort,
  ) -> None:
    """Capture the guard configuration; ``runtime`` and ``transformer`` are injected by Idunn."""
    self._guards: tuple[GuardFunction, ...] = guards
    self._implicit_return: bool = implicit_return
    self._strategy: GuardFailureEnum = strategy
    self._on_failure: Any = on_failure
    self._continuance: int = continuance

  def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
    """Apply the (optional) implicit-return rewrite, then wrap ``func`` with guard dispatch."""
    already_transformed: bool = getattr(func, '__implicit_return__', False)
    target: Callable[..., Any] = (
      self.transformer.transform_function(func)
      if self._implicit_return and not already_transformed
      else func
    )
    wrapped: Callable[..., Any] = self.runtime.wrap_function(
      target, self._guards, self._strategy, self._on_failure, self._continuance
    )
    if self._implicit_return:
      wrapped.__implicit_return__ = True  # type: ignore[attr-defined]
    return wrapped
