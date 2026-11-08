"""Lowering for ``eop_cond``: Elixir's ``cond`` as nested conditional expressions."""

from __future__ import annotations

import ast
from typing import Callable, NoReturn

from idunn import Adapter, LifecycleEnum

from modgud.domain.enums import EopFormEnum
from modgud.domain.errors import MarkerNotRewrittenError
from modgud.domain.ports import EopPort
from modgud.infrastructure.ast import ClauseReader


@Adapter(EopPort, key=EopFormEnum.COND, lifecycle=LifecycleEnum.SINGLETON)
class EopCondAdapter(EopPort):
  """Lower ``eop_cond`` in place to right-nested ``IfExp`` nodes; one temporary per call.

  As in Elixir, a test is true unless it is ``None`` or ``False``, so each test lowers to
  ``(t := test) is not None and t is not False``. Tests run in order and only the selected
  value, or ``default``, is evaluated.
  """

  def lower(
    self, call: ast.Call, *, hoistable: bool, fresh: Callable[[str], str]
  ) -> tuple[list[ast.stmt], ast.expr]:
    """Return no prelude and the conditional expression that replaces ``call``."""
    _, clauses, default = ClauseReader.read(call, EopFormEnum.COND, with_subject=False)
    temp: str = fresh('cond')
    expression: ast.expr = default
    for test, value in reversed(clauses):
      expression = ast.IfExp(test=self._is_truthy(temp, test), body=value, orelse=expression)
    return [], expression

  def refuse(self) -> NoReturn:
    """Raise for an ``eop_cond`` call that no decorator rewrote."""
    raise MarkerNotRewrittenError(EopFormEnum.COND)

  @staticmethod
  def _is_truthy(temp: str, test: ast.expr) -> ast.expr:
    """``(temp := test) is not None and temp is not False``."""
    bound: ast.expr = ast.NamedExpr(target=ast.Name(id=temp, ctx=ast.Store()), value=test)
    return ast.BoolOp(
      op=ast.And(),
      values=[
        ast.Compare(left=bound, ops=[ast.IsNot()], comparators=[ast.Constant(value=None)]),
        ast.Compare(
          left=ast.Name(id=temp, ctx=ast.Load()),
          ops=[ast.IsNot()],
          comparators=[ast.Constant(value=False)],
        ),
      ],
    )
