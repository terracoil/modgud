"""The three form adapters at unit level, with a deterministic ``fresh`` and no container."""

from __future__ import annotations

import ast
from typing import Callable

import pytest
from modgud import MarkerNotRewrittenError, MarkerUsageError
from modgud.infrastructure.adapters import EopCaseAdapter, EopCondAdapter, EopMatchAdapter

from tests.test_eop_patterns import Reserved, counter


def call_of(source: str) -> ast.Call:
  """Parse one form call with its markers reserved."""
  tree: ast.Module = Reserved().visit(ast.parse(source))
  statement: ast.stmt = tree.body[0]
  assert isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call)
  return statement.value


def lowered(source: str, adapter: object, *, hoistable: bool) -> tuple[list[ast.stmt], ast.expr]:
  """Lower ``source`` through ``adapter``."""
  lower: Callable[..., tuple[list[ast.stmt], ast.expr]] = adapter.lower
  prelude, expression = lower(call_of(source), hoistable=hoistable, fresh=counter())
  for statement in prelude:  # the real lowerer copies the call's location onto each one
    ast.fix_missing_locations(ast.copy_location(statement, ast.Pass(lineno=1, col_offset=0)))
  return prelude, ast.fix_missing_locations(expression)


class TestEopCondAdapter:
  def test_lowers_in_place_with_one_temporary(self) -> None:
    prelude, expression = lowered(
      "eop_cond(eop_clause(x < 0, 'neg'), eop_clause(x == 0, 'zero'), default='pos')",
      EopCondAdapter(),
      hoistable=False,
    )

    assert prelude == []
    assert ast.unparse(expression) == (
      "'neg' if (@mg_cond_1 := (x < 0)) is not None and @mg_cond_1 is not False "
      "else 'zero' if (@mg_cond_1 := (x == 0)) is not None and @mg_cond_1 is not False else 'pos'"
    )

  def test_refuses_a_missing_default(self) -> None:
    with pytest.raises(MarkerUsageError, match='needs default='):
      lowered("eop_cond(eop_clause(x < 0, 'neg'))", EopCondAdapter(), hoistable=False)

  def test_refuse_raises_the_call_time_error(self) -> None:
    with pytest.raises(MarkerNotRewrittenError, match='eop_cond only works'):
      EopCondAdapter().refuse()


class TestEopCaseAdapter:
  SOURCE = (
    'eop_case(shape, '
    "eop_clause(eop_when(Point(0, eop_var.y), eop_var.y > 0), f'above {eop_var.y}'), "
    "eop_clause(Point(eop_var.x, 0), eop_var.x), default='other')"
  )

  def test_hoisted_path_is_a_real_match_with_renamed_captures(self) -> None:
    prelude, expression = lowered(self.SOURCE, EopCaseAdapter(), hoistable=True)

    assert [type(statement).__name__ for statement in prelude] == ['FunctionDef', 'Match']
    assert ast.unparse(expression) == '@mg_case_1'
    match = prelude[1]
    assert isinstance(match, ast.Match)
    assert ast.unparse(match.cases[0].pattern) == 'Point(0, @mg_cap_0_y)'
    assert ast.unparse(match.cases[0].guard) == '@mg_guard_2(@mg_cap_0_y)'
    assert ast.unparse(match.cases[0].body[0]) == "@mg_case_1 = f'above {@mg_cap_0_y}'"
    assert ast.unparse(match.cases[1].body[0]) == '@mg_case_1 = @mg_cap_1_x'
    assert ast.unparse(match.cases[2].pattern) == '_'
    assert ast.unparse(match.cases[2].body[0]) == "@mg_case_1 = 'other'"

  def test_hoisted_guard_function_applies_the_elixir_rules(self) -> None:
    prelude, _ = lowered(self.SOURCE, EopCaseAdapter(), hoistable=True)

    assert ast.unparse(prelude[0]) == (
      'def @mg_guard_2(y):\n'
      '    try:\n'
      '        return (y > 0) is True\n'
      '    except Exception:\n'
      '        return False'
    )

  def test_matcher_path_defines_one_matcher_per_clause(self) -> None:
    prelude, expression = lowered(self.SOURCE, EopCaseAdapter(), hoistable=False)

    assert [type(statement).__name__ for statement in prelude] == ['FunctionDef', 'FunctionDef']
    assert ast.unparse(expression) == (
      "f'above {@mg_caps_2[0]}' if (@mg_caps_2 := @mg_match_5((@mg_subj_1 := shape))) is not None "
      'else @mg_caps_2[0] if (@mg_caps_2 := @mg_match_3(@mg_subj_1)) is not None '
      "else 'other'"
    )
    assert ast.unparse(prelude[0]) == (
      'def @mg_match_5(@mg_subj_6):\n'
      '    match @mg_subj_6:\n'
      '        case Point(0, y):\n'
      '            try:\n'
      '                @mg_ok_7 = (y > 0) is True\n'
      '            except Exception:\n'
      '                @mg_ok_7 = False\n'
      '            if @mg_ok_7:\n'
      '                return (y,)\n'
      '    return None'
    )

  def test_refuse_raises_the_call_time_error(self) -> None:
    with pytest.raises(MarkerNotRewrittenError, match='eop_case only works'):
      EopCaseAdapter().refuse()


class TestEopMatchAdapter:
  def test_lowers_to_a_boolean_matcher_call(self) -> None:
    prelude, expression = lowered(
      'eop_match(Point(0, eop_var._), shape)', EopMatchAdapter(), hoistable=False
    )

    assert ast.unparse(expression) == '@mg_match_1(shape)'
    assert ast.unparse(prelude[0]) == (
      'def @mg_match_1(@mg_subj_2):\n'
      '    match @mg_subj_2:\n'
      '        case Point(0, _):\n'
      '            return True\n'
      '    return False'
    )

  def test_a_bare_name_pattern_adds_an_equality_guard(self) -> None:
    prelude, _ = lowered('eop_match(limit, value)', EopMatchAdapter(), hoistable=False)

    assert 'case @mg_val_1 if @mg_val_1 == limit:' in ast.unparse(prelude[0])

  def test_refuses_the_wrong_arity(self) -> None:
    with pytest.raises(MarkerUsageError, match='exactly a pattern and a value'):
      lowered('eop_match(Point(0, 0))', EopMatchAdapter(), hoistable=False)

  def test_refuse_raises_the_call_time_error(self) -> None:
    with pytest.raises(MarkerNotRewrittenError, match='eop_match only works'):
      EopMatchAdapter().refuse()
