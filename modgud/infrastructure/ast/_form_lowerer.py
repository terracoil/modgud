"""Walk a function's statements and lower every ``eop_`` form through its port."""

from __future__ import annotations

import ast
from collections.abc import Mapping

from modgud.domain.enums import EopFormEnum
from modgud.domain.errors import MarkerPlacementError, MarkerUsageError
from modgud.domain.ports import EopPort

from ._form_call_lowerer import FormCallLowerer
from ._marker_resolver import MarkerResolver

_RESERVED_PREFIX: str = '@eop_'
_LEFTOVER_MESSAGES: dict[str, str] = {
  EopFormEnum.VAR.value: 'eop_var.<name> is usable only in the guard and value of the clause '
  'whose pattern binds <name>',
  EopFormEnum.WHEN.value: 'eop_when belongs at the top of an eop_case clause test or an '
  'eop_match pattern',
  EopFormEnum.CLAUSE.value: 'eop_clause belongs inside an eop_cond or eop_case call',
}


class FormLowerer:
  """Normalise marker references, lower each form call and place its prelude before its statement.

  Preludes are generated function definitions and, for a hoisted ``eop_case``, a real ``match``.
  They land in the same block as the statement, so a branch that never runs never defines them.
  """

  def __init__(self, forms: Mapping[EopFormEnum, EopPort], resolver: MarkerResolver) -> None:
    """Remember the ports and the resolver for this function."""
    self._forms: Mapping[EopFormEnum, EopPort] = forms
    self._resolver: MarkerResolver = resolver
    self._counter: int = 0

  def fresh(self, kind: str) -> str:
    """Return a temporary name no user code can spell."""
    self._counter += 1
    return f'@mg_{kind}_{self._counter}'

  def lower_function(self, fn_node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
    """Lower every form in ``fn_node`` in place.

    :raises MarkerUsageError: If a form is malformed, or marker vocabulary is left over.
    :raises MarkerPlacementError: If a form sits where it cannot be lowered.
    """
    if self._resolver.normalise(fn_node):
      fn_node.body = self._lower_block(fn_node.body)
      self._refuse_leftovers(fn_node)

  def _lower_block(self, body: list[ast.stmt]) -> list[ast.stmt]:
    lowered: list[ast.stmt] = []
    for statement in body:
      lowered.extend(self._lower_statement(statement))
    return lowered

  def _lower_statement(self, statement: ast.stmt) -> list[ast.stmt]:
    if isinstance(statement, ast.ClassDef):
      self._refuse_in_class(statement)
    for field in ('body', 'orelse', 'finalbody'):
      block: object = getattr(statement, field, None)
      if isinstance(block, list) and not isinstance(statement, ast.ClassDef):
        setattr(statement, field, self._lower_block(block))
    for handler in getattr(statement, 'handlers', []):
      handler.body = self._lower_block(handler.body)
    for case in getattr(statement, 'cases', []):
      case.body = self._lower_block(case.body)
    hoistable: ast.AST | None = (
      statement.value if isinstance(statement, (ast.Assign, ast.AnnAssign, ast.Expr)) else None
    )
    lowerer: FormCallLowerer = FormCallLowerer(self._forms, self.fresh, hoistable)
    lowerer.visit(statement)
    return [*lowerer.prelude, statement]

  @staticmethod
  def _refuse_in_class(statement: ast.ClassDef) -> None:
    for node in ast.walk(statement):
      if isinstance(node, ast.Name) and node.id.startswith(_RESERVED_PREFIX):
        raise MarkerPlacementError(
          f'{node.id[1:]} cannot be used inside a class body nested in a decorated function',
          node.lineno,
          node.col_offset,
        )

  @staticmethod
  def _refuse_leftovers(fn_node: ast.AST) -> None:
    for node in ast.walk(fn_node):
      if isinstance(node, ast.Name) and node.id.startswith(_RESERVED_PREFIX):
        name: str = node.id[1:]
        message: str = _LEFTOVER_MESSAGES.get(name, f'{name} is referenced but never called')
        raise MarkerUsageError(message, node.lineno, node.col_offset)
