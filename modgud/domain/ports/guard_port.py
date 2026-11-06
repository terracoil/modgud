"""Port describing the guard runtime the ``guarded_expression`` decorator consumes.

The implementation lives in ``modgud.infrastructure.adapters`` and is injected into the
decorator by Idunn (``@Invert``), so the app layer never imports infrastructure.
"""

from __future__ import annotations

from typing import Any, Callable, Protocol

from idunn import Port

# Not from modgud.domain: its __init__ re-exports this port.
from modgud.domain.enums import GuardFailureEnum
from modgud.domain.types import GuardFunction

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
  ) -> Callable[..., Any]:
    """Apply the (optional) implicit-return rewrite, then wrap ``func`` with guard dispatch."""
    ...
