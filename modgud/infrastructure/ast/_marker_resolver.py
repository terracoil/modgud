"""Recognise ``eop_`` markers by the object a name refers to, never by its spelling."""

from __future__ import annotations

import ast
import inspect
from collections.abc import Mapping
from types import CodeType, ModuleType
from typing import Any

from modgud.domain.enums import EopFormEnum
from modgud.domain.types import eop_clause

_MISSING: Any = object()


class MarkerResolver(ast.NodeTransformer):
  """Replace every reference to an ``eop_`` marker with its reserved ``@eop_`` name.

  A ``Name``, or an attribute chain through module objects, resolves against ``scope`` (the
  decorated function's closure, globals and builtins). A name bound anywhere inside the
  function is never a marker. The ``@`` in a reserved name makes it impossible to collide with
  user code, so the adapters can match on spelling afterwards.
  """

  def __init__(self, scope: Mapping[str, Any]) -> None:
    """Remember where names resolve."""
    super().__init__()
    self._scope: Mapping[str, Any] = scope
    self._bound: frozenset[str] = frozenset()
    self.found: set[EopFormEnum] = set()

  @staticmethod
  def reserved(form: EopFormEnum) -> str:
    """Return the reserved name the rewrite uses for ``form``."""
    return f'@{form.value}'

  @staticmethod
  def form_of(obj: object) -> EopFormEnum | None:
    """Return the form ``obj`` stands for, or ``None`` for an ordinary object."""
    form: EopFormEnum | None = None
    if obj is eop_clause:
      form = EopFormEnum.CLAUSE
    else:
      tag: object = inspect.getattr_static(type(obj), '__modgud_eop_form__', None)
      if isinstance(tag, EopFormEnum):
        form = tag
    return form

  def normalise(self, fn_node: ast.FunctionDef | ast.AsyncFunctionDef) -> set[EopFormEnum]:
    """Rewrite marker references inside ``fn_node`` in place and return the forms seen."""
    self._bound = self.bound_names(fn_node) - {fn_node.name}
    self.generic_visit(fn_node)
    return self.found

  def references(self, code: CodeType) -> bool:
    """Tell whether ``code`` or any nested code object names a marker; no source is read."""
    names: set[str] = set()
    pending: list[CodeType] = [code]
    while pending:
      current: CodeType = pending.pop()
      names.update(current.co_names, current.co_freevars)
      pending.extend(const for const in current.co_consts if isinstance(const, CodeType))
    objects: list[Any] = [self._scope.get(name, _MISSING) for name in names]
    modules: list[ModuleType] = [obj for obj in objects if isinstance(obj, ModuleType)]
    attributes: list[Any] = [
      getattr(module, name, _MISSING) for module in modules for name in names
    ]
    return any(self.form_of(obj) is not None for obj in (*objects, *attributes))

  def visit_Name(self, node: ast.Name) -> ast.AST:
    """Replace a bare marker reference."""
    form: EopFormEnum | None = self._resolve(node)
    return node if form is None else self._reserved_node(form, node)

  def visit_Attribute(self, node: ast.Attribute) -> ast.AST:
    """Replace a marker reached through modules, such as ``modgud.eop_cond``."""
    form: EopFormEnum | None = self._resolve(node)
    return self.generic_visit(node) if form is None else self._reserved_node(form, node)

  def _reserved_node(self, form: EopFormEnum, original: ast.expr) -> ast.Name:
    self.found.add(form)
    return ast.copy_location(ast.Name(id=self.reserved(form), ctx=ast.Load()), original)

  def _resolve(self, node: ast.expr) -> EopFormEnum | None:
    """Resolve ``node`` through the scope and module attributes; ``None`` when it is not a marker."""
    attrs: list[str] = []
    root: ast.expr = node
    while isinstance(root, ast.Attribute):
      attrs.append(root.attr)
      root = root.value
    resolvable: bool = (
      isinstance(root, ast.Name) and isinstance(root.ctx, ast.Load) and root.id not in self._bound
    )
    obj: Any = (
      self._scope.get(root.id, _MISSING) if resolvable and isinstance(root, ast.Name) else _MISSING
    )
    for attr in reversed(attrs):
      obj = getattr(obj, attr, _MISSING) if isinstance(obj, ModuleType) else _MISSING
    return None if obj is _MISSING else self.form_of(obj)

  @staticmethod
  def bound_names(root: ast.AST) -> frozenset[str]:
    """Return every name bound anywhere under ``root``: parameters, captures and nested scopes."""
    bound: set[str] = set()
    for node in ast.walk(root):
      if isinstance(node, ast.Name) and not isinstance(node.ctx, ast.Load):
        bound.add(node.id)
      elif isinstance(node, ast.arg):
        bound.add(node.arg)
      elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        bound.add(node.name)
      elif isinstance(node, ast.alias):
        bound.add((node.asname or node.name).split('.')[0])
      elif isinstance(node, ast.ExceptHandler) and node.name is not None:
        bound.add(node.name)
      elif isinstance(node, (ast.MatchAs, ast.MatchStar)) and node.name is not None:
        bound.add(node.name)
      elif isinstance(node, ast.MatchMapping) and node.rest is not None:
        bound.add(node.rest)
    return frozenset(bound)
