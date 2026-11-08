"""Port describing how one ``eop_`` form is lowered, and how it refuses to run un-rewritten.

One adapter per form implements it under its ``EopFormEnum`` key, so the app markers and the
implicit-return rewrite reach the right one through Idunn without naming it.
"""

from __future__ import annotations

import ast
from typing import Callable, NoReturn, Protocol

from idunn import Port


@Port
class EopPort(Protocol):
  """Lower one expression form, and refuse it when it runs as a plain call."""

  def lower(
    self, call: ast.Call, *, hoistable: bool, fresh: Callable[[str], str]
  ) -> tuple[list[ast.stmt], ast.expr]:
    """Return the statements to place before the enclosing statement, and the replacement expression.

    :param call: The form call, with marker references already normalised to ``@eop_`` names.
    :param hoistable: Whether evaluating the form before its statement keeps evaluation order.
    :param fresh: Returns a new temporary name for a given kind.
    :raises MarkerUsageError: If the call is malformed.
    :raises MarkerPlacementError: If the call sits where it cannot be lowered.
    """
    ...

  def refuse(self) -> NoReturn:
    """Raise ``MarkerNotRewrittenError`` naming this form."""
    ...
