"""Port describing the AST transformer behind implicit returns.

The implementation lives in ``modgud.infrastructure.adapters`` and is injected into the
``guarded_expression`` and ``implicit_return`` decorators by Idunn (``@Invert``), so the
app layer never imports infrastructure.
"""

from __future__ import annotations

from typing import Callable, Protocol

from idunn import Port

from modgud.domain.types import F, T


@Port
class ImplicitReturnPort(Protocol):
  """Transform a function so its tail expressions become implicit returns."""

  def transform(self, func: F) -> F:
    """Return ``func`` rewritten for implicit returns, as the ``implicit_return`` decorator sees it."""
    ...

  def transform_function(self, func: Callable[..., T]) -> Callable[..., T]:
    """Return the plain function `func` rewritten so the tail expressions become implicit returns."""
    ...
