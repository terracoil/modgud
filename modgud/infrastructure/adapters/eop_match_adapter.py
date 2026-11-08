"""Lowering for ``eop_match``: Elixir's ``match?`` as a generated matcher function."""

from __future__ import annotations

import ast
from typing import Callable, NoReturn

from idunn import Adapter, LifecycleEnum

from modgud.domain.enums import EopFormEnum
from modgud.domain.errors import MarkerNotRewrittenError, MarkerUsageError
from modgud.domain.ports import EopPort
from modgud.infrastructure.ast import (
  CaptureSubstituter,
  ClauseReader,
  MatcherBuilder,
  PatternTranslator,
)


@Adapter(EopPort, key=EopFormEnum.MATCH, lifecycle=LifecycleEnum.SINGLETON)
class EopMatchAdapter(EopPort):
  """Lower ``eop_match(pattern, value)`` to a call of a generated matcher returning a ``bool``.

  The matcher holds a real one-case ``match``, so captures never leak and no temporary is
  needed at the call site. A guard passes only when it is exactly ``True``; a guard that
  raises counts as no match, as in Elixir.
  """

  def lower(
    self, call: ast.Call, *, hoistable: bool, fresh: Callable[[str], str]
  ) -> tuple[list[ast.stmt], ast.expr]:
    """Return the matcher definition and the call that replaces ``call``."""
    starred: bool = any(isinstance(arg, ast.Starred) for arg in call.args)
    if len(call.args) != 2 or call.keywords or starred:
      raise MarkerUsageError(
        'eop_match takes exactly a pattern and a value', call.lineno, call.col_offset
      )
    pattern_expr, guard = ClauseReader.split_when(call.args[0])
    translator: PatternTranslator = PatternTranslator(self._same, fresh)
    pattern: ast.pattern = translator.translate(pattern_expr)
    names: dict[str, ast.expr] = {
      name: ast.Name(id=name, ctx=ast.Load()) for name in translator.captures
    }
    matcher: str = fresh('match')
    definition: ast.FunctionDef = MatcherBuilder.matcher_def(
      matcher,
      pattern,
      translator.value_tests,
      None if guard is None else CaptureSubstituter.substitute(guard, names),
      ast.Constant(value=True),
      ast.Constant(value=False),
      fresh,
    )
    replacement: ast.expr = ast.Call(
      func=ast.Name(id=matcher, ctx=ast.Load()), args=[call.args[1]], keywords=[]
    )
    return [definition], replacement

  def refuse(self) -> NoReturn:
    """Raise for an ``eop_match`` call that no decorator rewrote."""
    raise MarkerNotRewrittenError(EopFormEnum.MATCH)

  @staticmethod
  def _same(name: str) -> str:
    """Keep a capture's own name; the matcher is its own scope."""
    return name
