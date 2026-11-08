"""Lower every form call inside one statement, innermost first."""

from __future__ import annotations

import ast
from collections.abc import Mapping
from typing import Callable

from modgud.domain.enums import EopFormEnum
from modgud.domain.errors import MarkerPlacementError, MarkerUsageError
from modgud.domain.ports import EopPort

from ._marker_resolver import MarkerResolver

_FORMS: dict[str, EopFormEnum] = {
  f'@{form.value}': form for form in (EopFormEnum.COND, EopFormEnum.CASE, EopFormEnum.MATCH)
}


class FormCallLowerer(ast.NodeTransformer):
  """Replace each ``@eop_cond`` / ``@eop_case`` / ``@eop_match`` call through its port.

  Nested calls lower before their enclosing call. The statements each port hands back are
  collected in ``prelude``, for the caller to place before the statement. Two placement rules
  are checked here: a generated function may not read a name bound by an enclosing
  comprehension or lambda, and a lowering that needs a walrus may not sit in a comprehension's
  first iterable.
  """

  def __init__(
    self,
    forms: Mapping[EopFormEnum, EopPort],
    fresh: Callable[[str], str],
    hoistable_node: ast.AST | None,
  ) -> None:
    """Remember the ports, the name supply and which node may be evaluated early."""
    super().__init__()
    self._forms: Mapping[EopFormEnum, EopPort] = forms
    self._fresh: Callable[[str], str] = fresh
    self._hoistable_node: ast.AST | None = hoistable_node
    self._inner_names: list[set[str]] = []
    self._in_first_iterable: int = 0
    self.prelude: list[ast.stmt] = []

  def visit_Call(self, node: ast.Call) -> ast.AST:
    """Lower a form call after its arguments; leave any other call alone."""
    form: EopFormEnum | None = _FORMS.get(node.func.id) if isinstance(node.func, ast.Name) else None
    result: ast.AST
    if form is None:
      result = self.generic_visit(node)
    else:
      hoistable: bool = node is self._hoistable_node
      self.generic_visit(node)
      port: EopPort | None = self._forms.get(form)
      if port is None:
        raise MarkerUsageError(
          f'no port was supplied for {form.value}', node.lineno, node.col_offset
        )
      prelude, replacement = port.lower(node, hoistable=hoistable, fresh=self._fresh)
      self._check_placement(form, prelude, hoistable, node)
      for statement in prelude:
        ast.copy_location(statement, node)
      self.prelude.extend(prelude)
      result = ast.copy_location(replacement, node)
    return result

  def visit_Lambda(self, node: ast.Lambda) -> ast.AST:
    """Track the parameters a lambda binds while its body is lowered."""
    names: set[str] = {arg.arg for arg in ast.walk(node.args) if isinstance(arg, ast.arg)}
    self._inner_names.append(names)
    self.generic_visit(node)
    self._inner_names.pop()
    return node

  def visit_ListComp(self, node: ast.ListComp) -> ast.AST:
    """Lower a list comprehension with its scope rules."""
    return self._visit_comprehension(node)

  def visit_SetComp(self, node: ast.SetComp) -> ast.AST:
    """Lower a set comprehension with its scope rules."""
    return self._visit_comprehension(node)

  def visit_GeneratorExp(self, node: ast.GeneratorExp) -> ast.AST:
    """Lower a generator expression with its scope rules."""
    return self._visit_comprehension(node)

  def visit_DictComp(self, node: ast.DictComp) -> ast.AST:
    """Lower a dict comprehension with its scope rules."""
    return self._visit_comprehension(node)

  def _visit_comprehension(
    self, node: ast.ListComp | ast.SetComp | ast.GeneratorExp | ast.DictComp
  ) -> ast.AST:
    """Visit the first iterable in the enclosing scope, then the rest inside the comprehension."""
    first: ast.comprehension = node.generators[0]
    self._in_first_iterable += 1
    first.iter = self._expr(first.iter)
    self._in_first_iterable -= 1
    names: set[str] = {
      name.id
      for generator in node.generators
      for name in ast.walk(generator.target)
      if isinstance(name, ast.Name)
    }
    self._inner_names.append(names)
    first.ifs = [self._expr(test) for test in first.ifs]
    for generator in node.generators[1:]:
      generator.iter = self._expr(generator.iter)
      generator.ifs = [self._expr(test) for test in generator.ifs]
    if isinstance(node, ast.DictComp):
      node.key = self._expr(node.key)
      node.value = self._expr(node.value)
    else:
      node.elt = self._expr(node.elt)
    self._inner_names.pop()
    return node

  def _expr(self, node: ast.expr) -> ast.expr:
    result: ast.AST = self.visit(node)
    assert isinstance(result, ast.expr)
    return result

  def _check_placement(
    self, form: EopFormEnum, prelude: list[ast.stmt], hoistable: bool, node: ast.Call
  ) -> None:
    uses_walrus: bool = form is EopFormEnum.COND or (form is EopFormEnum.CASE and not hoistable)
    if uses_walrus and self._in_first_iterable:
      raise MarkerPlacementError(
        f"{form.value} cannot sit in a comprehension's first iterable; bind it to a name first",
        node.lineno,
        node.col_offset,
      )
    inner: set[str] = set().union(*self._inner_names) if self._inner_names else set()
    read: list[str] = [
      name.id
      for statement in prelude
      for name in ast.walk(statement)
      if isinstance(name, ast.Name)
      and isinstance(name.ctx, ast.Load)
      and name.id in inner - MarkerResolver.bound_names(statement)
    ]
    if read:
      raise MarkerPlacementError(
        f'{form.value}: a pattern or guard cannot read {read[0]!r}, which is bound by an '
        'enclosing comprehension or lambda; bind the value to a name outside it first',
        node.lineno,
        node.col_offset,
      )
