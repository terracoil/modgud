"""``PatternTranslator`` at unit level: one check per row of the pattern table."""

from __future__ import annotations

import ast
from typing import Callable

import pytest
from modgud import MarkerUsageError
from modgud.infrastructure.ast import PatternTranslator


class Reserved(ast.NodeTransformer):
  """Spell ``eop_var`` and friends the way the resolver leaves them: with a leading ``@``."""

  def visit_Name(self, node: ast.Name) -> ast.AST:
    """Reserve every ``eop_`` name."""
    if node.id.startswith('eop_'):
      node.id = f'@{node.id}'
    return node


def pattern_of(source: str) -> ast.expr:
  """Parse one expression written as a pattern."""
  tree: ast.Module = Reserved().visit(ast.parse(source))
  statement: ast.stmt = tree.body[0]
  assert isinstance(statement, ast.Expr)
  return statement.value


def same(name: str) -> str:
  """Keep capture names as they are."""
  return name


def counter() -> Callable[[str], str]:
  """Return a deterministic ``fresh``."""
  count: list[int] = [0]

  def fresh(kind: str) -> str:
    count[0] += 1
    return f'@mg_{kind}_{count[0]}'

  return fresh


class TestRows:
  @pytest.mark.parametrize(
    ('source', 'kind'),
    [
      ('eop_var.y', ast.MatchAs),
      ('eop_var._', ast.MatchAs),
      ('0', ast.MatchValue),
      ("'text'", ast.MatchValue),
      ('-1', ast.MatchValue),
      ('None', ast.MatchSingleton),
      ('True', ast.MatchSingleton),
      ('Color.RED', ast.MatchValue),
      ('limit', ast.MatchAs),
      ('Point(0, eop_var.y)', ast.MatchClass),
      ('Point(x=0, y=eop_var.y)', ast.MatchClass),
      ('[first, eop_var.second]', ast.MatchSequence),
      ('(a, *eop_var.rest)', ast.MatchSequence),
      ("{'key': eop_var.value, **eop_var.rest}", ast.MatchMapping),
    ],
  )
  def test_each_row_becomes_the_expected_pattern_node(self, source: str, kind: type) -> None:
    translator = PatternTranslator(same, counter())

    assert isinstance(translator.translate(pattern_of(source)), kind)

  def test_captures_are_listed_in_order(self) -> None:
    translator = PatternTranslator(same, counter())
    translator.translate(pattern_of('[Point(eop_var.a, eop_var._), *eop_var.rest, eop_var.z]'))

    assert translator.captures == ['a', 'rest', 'z']

  def test_captures_are_renamed_through_the_callback(self) -> None:
    translator = PatternTranslator(lambda name: f'@mg_cap_0_{name}', counter())
    pattern = translator.translate(pattern_of('eop_var.y'))

    assert isinstance(pattern, ast.MatchAs)
    assert pattern.name == '@mg_cap_0_y'
    assert translator.captures == ['y']

  def test_wildcard_binds_nothing(self) -> None:
    translator = PatternTranslator(same, counter())
    pattern = translator.translate(pattern_of('eop_var._'))

    assert isinstance(pattern, ast.MatchAs)
    assert pattern.name is None
    assert translator.captures == []

  def test_a_bare_name_becomes_a_temporary_and_an_equality_test(self) -> None:
    translator = PatternTranslator(same, counter())
    pattern = translator.translate(pattern_of('limit'))

    assert isinstance(pattern, ast.MatchAs)
    assert pattern.name == '@mg_val_1'
    assert len(translator.value_tests) == 1
    assert ast.unparse(translator.value_tests[0]) == '@mg_val_1 == limit'
    assert translator.captures == []

  def test_a_star_wildcard_binds_nothing(self) -> None:
    translator = PatternTranslator(same, counter())
    pattern = translator.translate(pattern_of('[eop_var.first, *eop_var._]'))

    assert isinstance(pattern, ast.MatchSequence)
    assert isinstance(pattern.patterns[1], ast.MatchStar)
    assert pattern.patterns[1].name is None
    assert translator.captures == ['first']

  def test_mapping_rest_is_recorded(self) -> None:
    translator = PatternTranslator(same, counter())
    pattern = translator.translate(pattern_of("{'id': eop_var.i, **eop_var.rest}"))

    assert isinstance(pattern, ast.MatchMapping)
    assert pattern.rest == 'rest'
    assert translator.captures == ['i', 'rest']


class TestRefusals:
  @pytest.mark.parametrize(
    ('source', 'message'),
    [
      ('Point(0, 0) | Point(1, 1)', 'one clause per alternative'),
      ('lambda: 1', 'Lambda is not a supported pattern'),
      ('eop_var.y.z', 'Attribute is not a supported pattern'),
      ('Point(eop_var.a, eop_var.a)', 'appears twice'),
      ('[*eop_var.a, *eop_var.b]', 'only one star'),
      ('[*other]', 'only `\\*eop_var.name`'),
      ('{key: eop_var.v}', 'literal or a dotted name'),
      ('{**eop_var._}', 'only `\\*\\*eop_var.name`'),
      ('Point(*args)', 'cannot unpack arguments'),
      ('Point(**kwargs)', 'cannot unpack keyword arguments'),
      ('make()(1)', 'name its class directly'),
      ('eop_when(eop_var.v, True)', 'eop_when cannot appear inside a pattern'),
    ],
  )
  def test_outside_the_subset(self, source: str, message: str) -> None:
    with pytest.raises(MarkerUsageError, match=message):
      PatternTranslator(same, counter()).translate(pattern_of(source))
