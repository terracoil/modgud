"""Turn an expression written as a pattern into a real ``ast.pattern``."""

from __future__ import annotations

import ast
from typing import Callable

from modgud.domain.enums import EopFormEnum
from modgud.domain.errors import MarkerUsageError

_VAR: str = f'@{EopFormEnum.VAR.value}'


class PatternTranslator:
  """Translate the pattern subset: captures, wildcards, literals, dotted and bare names,
  class, sequence and mapping patterns. One instance serves one clause.

  ``captures`` lists the user's capture names in order of appearance. ``value_tests`` holds the
  equality tests a bare name turns into, each reading a generated capture, so the caller
  appends them to the case guard.
  """

  def __init__(self, capture_name: Callable[[str], str], fresh: Callable[[str], str]) -> None:
    """Remember how captures are renamed and where temporaries come from."""
    self._capture_name: Callable[[str], str] = capture_name
    self._fresh: Callable[[str], str] = fresh
    self.captures: list[str] = []
    self.value_tests: list[ast.expr] = []

  def translate(self, expr: ast.expr) -> ast.pattern:
    """Return the pattern ``expr`` spells.

    :raises MarkerUsageError: If ``expr`` is outside the supported pattern subset.
    """
    pattern: ast.pattern
    if isinstance(expr, ast.Attribute) and self._is_capture(expr):
      pattern = self._capture(expr.attr, expr)
    elif isinstance(expr, ast.Constant):
      pattern = self._literal(expr)
    elif self._is_negative_number(expr):
      pattern = ast.MatchValue(value=expr)
    elif isinstance(expr, ast.Attribute) and self._is_dotted(expr):
      pattern = ast.MatchValue(value=expr)
    elif isinstance(expr, ast.Name) and not expr.id.startswith('@'):
      pattern = self._value_of_name(expr)
    elif isinstance(expr, ast.Call):
      pattern = self._class_pattern(expr)
    elif isinstance(expr, (ast.List, ast.Tuple)):
      pattern = self._sequence(expr)
    elif isinstance(expr, ast.Dict):
      pattern = self._mapping(expr)
    else:
      raise self._error(expr, self._unsupported_message(expr))
    return ast.copy_location(pattern, expr)

  @staticmethod
  def _unsupported_message(expr: ast.expr) -> str:
    message: str = f'{type(expr).__name__} is not a supported pattern'
    if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.BitOr):
      message = (
        'alternatives such as `A | B` are not patterns here; write one clause per alternative'
      )
    elif isinstance(expr, ast.Name):
      message = f'{expr.id[1:]} cannot appear inside a pattern'
    return message

  @staticmethod
  def _error(node: ast.AST, message: str) -> MarkerUsageError:
    return MarkerUsageError(
      message, getattr(node, 'lineno', None), getattr(node, 'col_offset', None)
    )

  @staticmethod
  def _is_capture(expr: ast.expr) -> bool:
    return (
      isinstance(expr, ast.Attribute) and isinstance(expr.value, ast.Name) and expr.value.id == _VAR
    )

  @staticmethod
  def _is_negative_number(expr: ast.expr) -> bool:
    return (
      isinstance(expr, ast.UnaryOp)
      and isinstance(expr.op, ast.USub)
      and isinstance(expr.operand, ast.Constant)
      and isinstance(expr.operand.value, (int, float, complex))
      and not isinstance(expr.operand.value, bool)
    )

  @classmethod
  def _is_dotted(cls, expr: ast.expr) -> bool:
    """Tell whether ``expr`` is a ``Name`` or an attribute chain rooted at one, not reserved."""
    root: ast.expr = expr
    while isinstance(root, ast.Attribute):
      root = root.value
    return isinstance(root, ast.Name) and not root.id.startswith('@')

  def _capture(self, name: str, node: ast.expr) -> ast.pattern:
    pattern: ast.pattern = ast.MatchAs(pattern=None, name=None)
    if name != '_':
      if name in self.captures:
        raise self._error(node, f'capture {name!r} appears twice in one pattern')
      self.captures.append(name)
      pattern = ast.MatchAs(pattern=None, name=self._capture_name(name))
    return pattern

  @staticmethod
  def _literal(expr: ast.Constant) -> ast.pattern:
    pattern: ast.pattern = ast.MatchValue(value=expr)
    if expr.value is None or isinstance(expr.value, bool):
      pattern = ast.MatchSingleton(value=expr.value)
    return pattern

  def _value_of_name(self, expr: ast.Name) -> ast.pattern:
    """Compare a bare name by value: capture into a temporary and test it in the guard."""
    temp: str = self._fresh('val')
    test: ast.expr = ast.Compare(
      left=ast.Name(id=temp, ctx=ast.Load()), ops=[ast.Eq()], comparators=[expr]
    )
    self.value_tests.append(ast.copy_location(test, expr))
    return ast.MatchAs(pattern=None, name=temp)

  def _class_pattern(self, expr: ast.Call) -> ast.pattern:
    if isinstance(expr.func, ast.Name) and expr.func.id.startswith('@'):
      raise self._error(expr, f'{expr.func.id[1:]} cannot appear inside a pattern')
    if not self._is_dotted(expr.func):
      raise self._error(expr, 'a class pattern must name its class directly')
    if any(isinstance(arg, ast.Starred) for arg in expr.args):
      raise self._error(expr, 'a class pattern cannot unpack arguments')
    if any(keyword.arg is None for keyword in expr.keywords):
      raise self._error(expr, 'a class pattern cannot unpack keyword arguments')
    return ast.MatchClass(
      cls=expr.func,
      patterns=[self.translate(arg) for arg in expr.args],
      kwd_attrs=[str(keyword.arg) for keyword in expr.keywords],
      kwd_patterns=[self.translate(keyword.value) for keyword in expr.keywords],
    )

  def _sequence(self, expr: ast.List | ast.Tuple) -> ast.pattern:
    patterns: list[ast.pattern] = []
    for element in expr.elts:
      if isinstance(element, ast.Starred):
        if not self._is_capture(element.value):
          raise self._error(element, 'only `*eop_var.name` or `*eop_var._` can star a sequence')
        if any(isinstance(pattern, ast.MatchStar) for pattern in patterns):
          raise self._error(element, 'a sequence pattern can hold only one star')
        patterns.append(self._star(element.value, element))
      else:
        patterns.append(self.translate(element))
    return ast.MatchSequence(patterns=patterns)

  def _star(self, capture: ast.expr, node: ast.expr) -> ast.MatchStar:
    assert isinstance(capture, ast.Attribute)
    name: str | None = None
    if capture.attr != '_':
      if capture.attr in self.captures:
        raise self._error(node, f'capture {capture.attr!r} appears twice in one pattern')
      self.captures.append(capture.attr)
      name = self._capture_name(capture.attr)
    return ast.copy_location(ast.MatchStar(name=name), node)

  def _mapping(self, expr: ast.Dict) -> ast.pattern:
    keys: list[ast.expr] = []
    patterns: list[ast.pattern] = []
    rest: str | None = None
    for key, value in zip(expr.keys, expr.values, strict=True):
      if key is None:
        if not self._is_capture(value) or getattr(value, 'attr', '_') == '_':
          raise self._error(value, 'only `**eop_var.name` can collect the remaining keys')
        rest = self._star(value, value).name
      elif isinstance(key, ast.Constant) or (
        isinstance(key, ast.Attribute) and self._is_dotted(key)
      ):
        keys.append(key)
        patterns.append(self.translate(value))
      else:
        raise self._error(key, 'a mapping pattern key must be a literal or a dotted name')
    return ast.MatchMapping(keys=keys, patterns=patterns, rest=rest)
