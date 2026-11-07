"""Port describing the AST transformer behind implicit returns.

The implementation lives in ``modgud.infrastructure.adapters`` and is injected into the
``guarded_expression`` and ``implicit_return`` decorators by Idunn (``@Invert``), so the
app layer never imports infrastructure.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Callable, Protocol

from idunn import Port

# Not from modgud.domain: its __init__ re-exports this port.
from modgud.domain.enums import EopFormEnum
from modgud.domain.types import F, T

from .eop_port import EopPort


@Port
class ImplicitReturnPort(Protocol):
  """Transform a function so its tail expressions become implicit returns."""

  def transform(self, func: F, *, forms: Mapping[EopFormEnum, EopPort]) -> F:
    """Return ``func`` rewritten for implicit returns, as the ``implicit_return`` decorator sees it.

    Every ``eop_`` form in the body is lowered through its port in ``forms``.
    """
    ...

  def transform_function(
    self,
    func: Callable[..., T],
    *,
    forms: Mapping[EopFormEnum, EopPort],
    implicit_return: bool = True,
  ) -> Callable[..., T]:
    """Return the plain function ``func`` rewritten so the tail expressions become implicit returns.

    With ``implicit_return=False`` only the ``eop_`` forms are lowered, explicit ``return``
    statements stay, and a function that references no form comes back unchanged.
    """
    ...
