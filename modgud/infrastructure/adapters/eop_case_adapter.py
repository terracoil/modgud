"""Lowering for ``eop_case``: Elixir's ``case`` as a hoisted ``match`` or generated matchers."""

from __future__ import annotations

import ast
import functools
from typing import Callable, NoReturn

from idunn import Adapter, LifecycleEnum

from modgud.domain.enums import EopFormEnum
from modgud.domain.errors import MarkerNotRewrittenError
from modgud.domain.ports import EopPort
from modgud.infrastructure.ast import (
  CaptureSubstituter,
  ClauseReader,
  MatcherBuilder,
  PatternTranslator,
)

Clause = tuple[ast.expr, ast.expr | None, ast.expr]  # (pattern, guard, value)


@Adapter(EopPort, key=EopFormEnum.CASE, lifecycle=LifecycleEnum.SINGLETON)
class EopCaseAdapter(EopPort):
  """Lower ``eop_case`` two ways, both with exact ``match`` semantics.

  When the call is a whole statement's value it becomes a real ``match`` placed before the
  statement, at native speed, with captures renamed so nothing leaks. Anywhere else each
  clause becomes a generated matcher returning its captures, and the call becomes a chain of
  conditional expressions, so the form works in comprehensions, lambdas and operands. A guard
  passes only when it is exactly ``True``; a guard that raises counts as no match, as in Elixir.
  """

  def lower(
    self, call: ast.Call, *, hoistable: bool, fresh: Callable[[str], str]
  ) -> tuple[list[ast.stmt], ast.expr]:
    """Return the prelude and the expression that replace ``call``."""
    subject, raw_clauses, default = ClauseReader.read(call, EopFormEnum.CASE, with_subject=True)
    assert subject is not None
    clauses: list[Clause] = [(*ClauseReader.split_when(test), value) for test, value in raw_clauses]
    return (
      self._hoisted(subject, clauses, default, fresh)
      if hoistable
      else self._matchers(subject, clauses, default, fresh)
    )

  def refuse(self) -> NoReturn:
    """Raise for an ``eop_case`` call that no decorator rewrote."""
    raise MarkerNotRewrittenError(EopFormEnum.CASE)

  @classmethod
  def _hoisted(
    cls, subject: ast.expr, clauses: list[Clause], default: ast.expr, fresh: Callable[[str], str]
  ) -> tuple[list[ast.stmt], ast.expr]:
    """One real ``match`` assigning a temporary; guards become small generated functions."""
    result: str = fresh('case')
    prelude: list[ast.stmt] = []
    cases: list[ast.match_case] = []
    for index, (pattern_expr, guard, value) in enumerate(clauses):
      translator: PatternTranslator = PatternTranslator(
        functools.partial(cls._renamed, index), fresh
      )
      pattern: ast.pattern = translator.translate(pattern_expr)
      renamed: dict[str, ast.expr] = {
        name: ast.Name(id=cls._renamed(index, name), ctx=ast.Load()) for name in translator.captures
      }
      tests: list[ast.expr] = list(translator.value_tests)
      if guard is not None:
        guard_name: str = fresh('guard')
        plain: dict[str, ast.expr] = {
          name: ast.Name(id=name, ctx=ast.Load()) for name in translator.captures
        }
        prelude.append(
          MatcherBuilder.guard_def(
            guard_name, translator.captures, CaptureSubstituter.substitute(guard, plain)
          )
        )
        tests.append(
          ast.Call(
            func=ast.Name(id=guard_name, ctx=ast.Load()),
            args=list(renamed.values()),
            keywords=[],
          )
        )
      body: list[ast.stmt] = [cls._assign(result, CaptureSubstituter.substitute(value, renamed))]
      cases.append(
        ast.match_case(pattern=pattern, guard=MatcherBuilder.conjunction(tests), body=body)
      )
    cases.append(
      ast.match_case(
        pattern=ast.MatchAs(pattern=None, name=None),
        guard=None,
        body=[cls._assign(result, default)],
      )
    )
    prelude.append(ast.Match(subject=subject, cases=cases))
    return prelude, ast.Name(id=result, ctx=ast.Load())

  @classmethod
  def _matchers(
    cls, subject: ast.expr, clauses: list[Clause], default: ast.expr, fresh: Callable[[str], str]
  ) -> tuple[list[ast.stmt], ast.expr]:
    """One generated matcher per clause and a chain of conditional expressions."""
    subject_temp: str = fresh('subj')
    captures_temp: str = fresh('caps')
    prelude: list[ast.stmt] = []
    expression: ast.expr = default
    for index in reversed(range(len(clauses))):
      pattern_expr, guard, value = clauses[index]
      translator: PatternTranslator = PatternTranslator(cls._same, fresh)
      pattern: ast.pattern = translator.translate(pattern_expr)
      plain: dict[str, ast.expr] = {
        name: ast.Name(id=name, ctx=ast.Load()) for name in translator.captures
      }
      matcher: str = fresh('match')
      prelude.insert(
        0,
        MatcherBuilder.matcher_def(
          matcher,
          pattern,
          translator.value_tests,
          None if guard is None else CaptureSubstituter.substitute(guard, plain),
          ast.Tuple(elts=list(plain.values()), ctx=ast.Load()),
          ast.Constant(value=None),
          fresh,
        ),
      )
      indexed: dict[str, ast.expr] = {
        name: ast.Subscript(
          value=ast.Name(id=captures_temp, ctx=ast.Load()),
          slice=ast.Constant(value=position),
          ctx=ast.Load(),
        )
        for position, name in enumerate(translator.captures)
      }
      subject_ref: ast.expr = (
        ast.NamedExpr(target=ast.Name(id=subject_temp, ctx=ast.Store()), value=subject)
        if index == 0
        else ast.Name(id=subject_temp, ctx=ast.Load())
      )
      test: ast.expr = ast.Compare(
        left=ast.NamedExpr(
          target=ast.Name(id=captures_temp, ctx=ast.Store()),
          value=ast.Call(
            func=ast.Name(id=matcher, ctx=ast.Load()), args=[subject_ref], keywords=[]
          ),
        ),
        ops=[ast.IsNot()],
        comparators=[ast.Constant(value=None)],
      )
      expression = ast.IfExp(
        test=test, body=CaptureSubstituter.substitute(value, indexed), orelse=expression
      )
    return prelude, expression

  @staticmethod
  def _renamed(index: int, name: str) -> str:
    """Return the function-local name a hoisted clause's capture is bound to."""
    return f'@mg_cap_{index}_{name}'

  @staticmethod
  def _same(name: str) -> str:
    """Keep a capture's own name; a matcher is its own scope."""
    return name

  @staticmethod
  def _assign(name: str, value: ast.expr) -> ast.Assign:
    return ast.Assign(targets=[ast.Name(id=name, ctx=ast.Store())], value=value)
