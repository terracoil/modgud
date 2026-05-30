"""Protocol describing the ImplicitReturnTransformer contract.

The concrete implementation lives in `modgud.infrastructure.implicit_ret`.
This Protocol exists so the app layer can be wired through IoC (gleipnyr)
without depending on the infrastructure module directly. For now the
decorators still import the concrete class; the Protocol just documents
the shape they consume.
"""

from __future__ import annotations

from typing import Callable, Protocol, TypeVar

T = TypeVar('T')


class ImplicitReturnTransformerPort(Protocol):
  """Transform a function so its tail expressions become implicit returns."""

  @classmethod
  def transform_function(cls, func: Callable[..., T]) -> Callable[..., T]:
    """Return `func` rewritten so the tail expressions become implicit returns."""
    ...
