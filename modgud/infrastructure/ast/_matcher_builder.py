"""Build the generated functions behind ``eop_case`` and ``eop_match``."""

from __future__ import annotations

import ast
from typing import Callable


class MatcherBuilder:
  """Generate the small functions the pattern forms lower to.

  As in Elixir, a guard passes only when it is exactly ``True``, and a guard that raises an
  ``Exception`` counts as no match. Both rules live in the ``try`` these builders emit.
  """

  @staticmethod
  def function(name: str, params: list[str], body: list[ast.stmt]) -> ast.FunctionDef:
    """Return ``def name(*params): body``."""
    node: ast.FunctionDef = ast.FunctionDef(
      name=name,
      args=ast.arguments(
        posonlyargs=[],
        args=[ast.arg(arg=param) for param in params],
        vararg=None,
        kwonlyargs=[],
        kw_defaults=[],
        kwarg=None,
        defaults=[],
      ),
      body=body,
      decorator_list=[],
      returns=None,
    )
    node.type_params = []  # type: ignore[attr-defined]  # required from 3.12, harmless before
    return node

  @classmethod
  def guard_def(cls, name: str, params: list[str], guard: ast.expr) -> ast.FunctionDef:
    """Return a guard function: ``True`` only when ``guard`` is exactly ``True`` and did not raise."""
    body: list[ast.stmt] = [
      ast.Try(
        body=[ast.Return(value=cls._is_true(guard))],
        handlers=[cls._handler([ast.Return(value=ast.Constant(value=False))])],
        orelse=[],
        finalbody=[],
      )
    ]
    return cls.function(name, params, body)

  @classmethod
  def matcher_def(
    cls,
    name: str,
    pattern: ast.pattern,
    value_tests: list[ast.expr],
    guard: ast.expr | None,
    hit: ast.expr,
    miss: ast.expr,
    fresh: Callable[[str], str],
  ) -> ast.FunctionDef:
    """Return a matcher: a one-case ``match`` that returns ``hit`` on a match, else ``miss``."""
    subject: str = fresh('subj')
    body: list[ast.stmt] = [ast.Return(value=hit)]
    if guard is not None:
      ok: str = fresh('ok')
      body = [
        ast.Try(
          body=[cls._assign(ok, cls._is_true(guard))],
          handlers=[cls._handler([cls._assign(ok, ast.Constant(value=False))])],
          orelse=[],
          finalbody=[],
        ),
        ast.If(test=ast.Name(id=ok, ctx=ast.Load()), body=[ast.Return(value=hit)], orelse=[]),
      ]
    case: ast.match_case = ast.match_case(
      pattern=pattern, guard=cls.conjunction(value_tests), body=body
    )
    statements: list[ast.stmt] = [
      ast.Match(subject=ast.Name(id=subject, ctx=ast.Load()), cases=[case]),
      ast.Return(value=miss),
    ]
    return cls.function(name, [subject], statements)

  @staticmethod
  def conjunction(tests: list[ast.expr]) -> ast.expr | None:
    """Return ``tests`` joined with ``and``, or ``None`` when there are none."""
    joined: ast.expr | None = None
    if len(tests) == 1:
      joined = tests[0]
    elif tests:
      joined = ast.BoolOp(op=ast.And(), values=list(tests))
    return joined

  @staticmethod
  def _is_true(guard: ast.expr) -> ast.expr:
    return ast.Compare(left=guard, ops=[ast.Is()], comparators=[ast.Constant(value=True)])

  @staticmethod
  def _assign(name: str, value: ast.expr) -> ast.Assign:
    return ast.Assign(targets=[ast.Name(id=name, ctx=ast.Store())], value=value)

  @staticmethod
  def _handler(body: list[ast.stmt]) -> ast.ExceptHandler:
    return ast.ExceptHandler(type=ast.Name(id='Exception', ctx=ast.Load()), name=None, body=body)
