"""Replace ``eop_var.name`` references with the expression that holds the capture."""

from __future__ import annotations

import ast
import copy
from collections.abc import Mapping

from modgud.domain.enums import EopFormEnum

_VAR: str = f'@{EopFormEnum.VAR.value}'


class CaptureSubstituter(ast.NodeTransformer):
  """Swap ``@eop_var.<name>`` for ``mapping[name]``; names outside the mapping are left alone.

  A nested form lowers before its enclosing one, so a capture it does not bind must stay for
  the enclosing clause to substitute. Whatever is still unbound at the end is refused.
  """

  def __init__(self, mapping: Mapping[str, ast.expr]) -> None:
    """Remember which capture each name stands for."""
    super().__init__()
    self._mapping: Mapping[str, ast.expr] = mapping

  @classmethod
  def substitute(cls, expr: ast.expr, mapping: Mapping[str, ast.expr]) -> ast.expr:
    """Return ``expr`` with every bound capture replaced; the original is not modified."""
    result: ast.AST = cls(mapping).visit(copy.deepcopy(expr))
    assert isinstance(result, ast.expr)
    return result

  def visit_Attribute(self, node: ast.Attribute) -> ast.AST:
    """Replace a capture reference, or keep walking."""
    is_capture: bool = (
      isinstance(node.value, ast.Name) and node.value.id == _VAR and node.attr in self._mapping
    )
    return (
      ast.copy_location(copy.deepcopy(self._mapping[node.attr]), node)
      if is_capture
      else self.generic_visit(node)
    )
