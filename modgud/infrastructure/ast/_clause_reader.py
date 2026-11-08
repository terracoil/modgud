"""Read the arguments of a form call: subject, ``eop_clause`` items, ``default=`` and ``eop_when``."""

from __future__ import annotations

import ast

from modgud.domain.enums import EopFormEnum
from modgud.domain.errors import MarkerUsageError

_CLAUSE: str = f'@{EopFormEnum.CLAUSE.value}'
_WHEN: str = f'@{EopFormEnum.WHEN.value}'


class ClauseReader:
  """Validate a form call's shape and hand back its parts as expressions."""

  @classmethod
  def read(
    cls, call: ast.Call, form: EopFormEnum, *, with_subject: bool
  ) -> tuple[ast.expr | None, list[tuple[ast.expr, ast.expr]], ast.expr]:
    """Return ``(subject, [(test, value), ...], default)`` for ``call``.

    :raises MarkerUsageError: For a starred argument, a clause that is not a literal
      ``eop_clause(...)`` call, a missing subject, zero clauses, or a keyword other than
      a single ``default=``.
    """
    name: str = form.value
    positional: list[ast.expr] = list(call.args)
    if any(isinstance(arg, ast.Starred) for arg in positional):
      raise cls._error(call, f'{name} clauses must be written in the call, not unpacked')
    subject: ast.expr | None = None
    if with_subject:
      if not positional:
        raise cls._error(call, f'{name} needs a subject as its first argument')
      subject = positional.pop(0)
    clauses: list[tuple[ast.expr, ast.expr]] = [cls._clause(arg, name) for arg in positional]
    if not clauses:
      raise cls._error(call, f'{name} needs at least one eop_clause')
    defaults: list[ast.expr] = [kw.value for kw in call.keywords if kw.arg == 'default']
    others: list[str] = [str(kw.arg) for kw in call.keywords if kw.arg != 'default']
    if others:
      raise cls._error(call, f'{name} accepts only default=, not {", ".join(others)}')
    if len(defaults) != 1:
      raise cls._error(call, f'{name} needs default=; it is the value when no clause is selected')
    return subject, clauses, defaults[0]

  @classmethod
  def split_when(cls, test: ast.expr) -> tuple[ast.expr, ast.expr | None]:
    """Return ``(pattern, guard)`` from ``eop_when(pattern, guard)``, or ``(test, None)``."""
    pattern: ast.expr = test
    guard: ast.expr | None = None
    if isinstance(test, ast.Call) and isinstance(test.func, ast.Name) and test.func.id == _WHEN:
      if (
        len(test.args) != 2
        or test.keywords
        or any(isinstance(arg, ast.Starred) for arg in test.args)
      ):
        raise cls._error(test, 'eop_when takes exactly a pattern and a guard')
      pattern, guard = test.args
      cls._refuse_scope_effects(guard)
    return pattern, guard

  @classmethod
  def _refuse_scope_effects(cls, guard: ast.expr) -> None:
    """Refuse await, yield and ``:=`` in a guard, which runs inside a generated function."""
    for node in ast.walk(guard):
      if isinstance(node, (ast.Await, ast.Yield, ast.YieldFrom, ast.NamedExpr)):
        raise cls._error(
          node,
          'an eop_when guard cannot contain await, yield or :=; as in Elixir, a guard is a test',
        )

  @classmethod
  def _clause(cls, arg: ast.expr, name: str) -> tuple[ast.expr, ast.expr]:
    is_clause: bool = (
      isinstance(arg, ast.Call) and isinstance(arg.func, ast.Name) and arg.func.id == _CLAUSE
    )
    if not is_clause:
      raise cls._error(arg, f'each {name} argument must be a literal eop_clause(test, value)')
    assert isinstance(arg, ast.Call)
    parts: dict[str, ast.expr] = dict(zip(('test', 'value'), arg.args, strict=False))
    for keyword in arg.keywords:
      if keyword.arg not in ('test', 'value') or keyword.arg in parts:
        raise cls._error(arg, 'eop_clause takes exactly a test and a value')
      parts[keyword.arg] = keyword.value
    if len(arg.args) > 2 or set(parts) != {'test', 'value'}:
      raise cls._error(arg, 'eop_clause takes exactly a test and a value')
    return parts['test'], parts['value']

  @staticmethod
  def _error(node: ast.AST, message: str) -> MarkerUsageError:
    return MarkerUsageError(
      message, getattr(node, 'lineno', None), getattr(node, 'col_offset', None)
    )
