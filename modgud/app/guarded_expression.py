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

from modgud.domain.enums import EopFormEnum, GuardFailureEnum
from modgud.domain.errors import GuardClauseError
from modgud.domain.ports import EopPort, GuardPort, ImplicitReturnPort
from modgud.domain.types import GuardFunction


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
  ``guard_port``, ``imp_return_port`` and the three ``eop_*_port`` ports are injected by Idunn,
  which discovers modgud's adapters the first time a decoration leaves one of them to it. Pass
  a port explicitly to substitute a different implementation (e.g. a test fake); pass all five
  and nothing is discovered at all.
  """

  guard_port: GuardPort  # assigned by @Invert
  imp_return_port: ImplicitReturnPort  # assigned by @Invert
  eop_cond_port: EopPort  # assigned by @Invert
  eop_case_port: EopPort  # assigned by @Invert
  eop_match_port: EopPort  # assigned by @Invert

  # @Invert assigns the port parameters to self before the body runs.
  # noinspection PyUnusedLocal
  @Invert(
    bootstrap='modgud',
    keys={
      'eop_cond_port': EopFormEnum.COND,
      'eop_case_port': EopFormEnum.CASE,
      'eop_match_port': EopFormEnum.MATCH,
    },
  )
  def __init__(
    self,
    *guards: GuardFunction,
    implicit_return: bool = True,
    strategy: GuardFailureEnum = GuardFailureEnum.ERROR_RAISE,
    on_failure: Any = GuardClauseError,
    continuance: int = 0,
    guard_port: GuardPort,
    imp_return_port: ImplicitReturnPort,
    eop_cond_port: EopPort,
    eop_case_port: EopPort,
    eop_match_port: EopPort,
  ) -> None:
    """Capture the guard configuration; the ports are injected by Idunn or passed by the caller."""
    self._guards: tuple[GuardFunction, ...] = guards
    self._implicit_return: bool = implicit_return
    self._strategy: GuardFailureEnum = strategy
    self._on_failure: Any = on_failure
    self._continuance: int = continuance

  def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
    """Hand ``func`` to the guard port, which rewrites it (optionally) and wraps it with guards.

    ``func`` may also be a ``staticmethod`` / ``classmethod`` object (modgud applied outside
    the built-in); the result is then a descriptor of the same kind.
    """
    return self.guard_port.transform(
      func,
      continuance=self._continuance,
      imp_return_port=self.imp_return_port,
      implicit_return=self._implicit_return,
      guards=self._guards,
      strategy=self._strategy,
      on_failure=self._on_failure,
      forms=self._forms(),
    )

  def _forms(self) -> dict[EopFormEnum, EopPort]:
    """Map each form to the port that lowers it."""
    return {
      EopFormEnum.COND: self.eop_cond_port,
      EopFormEnum.CASE: self.eop_case_port,
      EopFormEnum.MATCH: self.eop_match_port,
    }
