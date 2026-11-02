"""Port describing the AST transformer behind implicit returns.

The implementation lives in ``modgud.infrastructure.adapters`` and is injected into the
``guarded_expression`` and ``implicit_return`` decorators by Idunn (``@Invert``), so the
app layer never imports infrastructure.
"""

from __future__ import annotations

from typing import Callable, Protocol, TypeVar

from idunn import Port

T = TypeVar('T')


@Port
class ImplicitReturnTransformerPort(Protocol):
  """Transform a function so its tail expressions become implicit returns."""

  @classmethod
  def transform_function(cls, func: Callable[..., T]) -> Callable[..., T]:
    """Return `func` rewritten so the tail expressions become implicit returns."""
    ...
