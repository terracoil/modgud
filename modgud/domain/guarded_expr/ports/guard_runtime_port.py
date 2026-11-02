"""Port describing the guard runtime the ``guarded_expression`` decorator consumes.

The implementation lives in ``modgud.infrastructure.adapters`` and is injected into the
decorator by Idunn (``@Invert``), so the app layer never imports infrastructure.
"""

from __future__ import annotations

from typing import Any, Callable, Protocol

from idunn import Port

from modgud.domain.guarded_expr import GuardFailureEnum, GuardFunction


@Port
class GuardRuntimePort(Protocol):
  """Wrap a callable with guard evaluation + failure dispatch."""

  def wrap_function(
    self,
    func: Callable[..., Any],
    guards: tuple[GuardFunction, ...],
    strategy: GuardFailureEnum,
    on_failure: Any,
    continuance: int,
  ) -> Callable[..., Any]:
    """Return `func` wrapped with guard evaluation + failure dispatch.

    Contract for methods: when ``func`` is defined in a class body and its first positional
    parameter is named ``self`` or ``cls``, the guards receive the call's arguments without
    that receiver. ``CALL_HANDLER`` handlers still receive the full argument list. A
    coroutine function is wrapped in a coroutine function, so failures surface at ``await``.
    """
    ...
