"""Port describing the guard runtime the ``guarded_expression`` decorator consumes.

The implementation lives in ``modgud.infrastructure.adapters`` and is injected into the
decorator by Idunn (``@Invert``), so the app layer never imports infrastructure.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Callable, Protocol

from idunn import Port

# Not from modgud.domain: its __init__ re-exports this port.
from modgud.domain.enums import EopFormEnum, GuardFailureEnum
from modgud.domain.types import GuardFunction

from .eop_port import EopPort
from .implicit_return_port import ImplicitReturnPort


@Port
class GuardPort(Protocol):
  """Rewrite a callable for implicit returns, then wrap it with guard evaluation + failure dispatch."""

  def transform(
    self,
    func: Callable[..., Any],
    continuance: int,
    imp_return_port: ImplicitReturnPort,
    implicit_return: bool,
    guards: tuple[GuardFunction, ...],
    strategy: GuardFailureEnum,
    on_failure: Any,
    forms: Mapping[EopFormEnum, EopPort],
  ) -> Callable[..., Any]:
    """Apply the implicit-return rewrite and the ``eop_`` lowering, then wrap ``func`` with guards.

    ``forms`` maps each form to the port that lowers it; it is handed to ``imp_return_port``.
    """
    ...
