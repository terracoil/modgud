"""Protocol describing the GuardRuntime contract.

The concrete implementation lives in `modgud.infrastructure.guarded_expr`.
This Protocol exists so the app layer can be wired through IoC (gleipnyr)
without depending on the infrastructure module directly. For now the
decorators still import the concrete class; the Protocol just documents
the shape they consume.
"""

from __future__ import annotations

from typing import Any, Callable, Protocol

from modgud.domain.guarded_expr import GuardFailureStrategy
from modgud.shared import GuardFunction


class GuardRuntimePort(Protocol):
  """Wrap a callable with guard evaluation + failure dispatch."""

  @classmethod
  def wrap_function(
    cls,
    func: Callable[..., Any],
    guards: tuple[GuardFunction, ...],
    strategy: GuardFailureStrategy,
    on_failure: Any,
    continuance: int,
  ) -> Callable[..., Any]:
    """Return `func` wrapped with guard evaluation + failure dispatch."""
    ...
