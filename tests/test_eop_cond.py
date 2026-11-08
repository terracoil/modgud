"""``eop_cond`` end to end: order, laziness, Elixir truth, positions, modes and methods."""

from __future__ import annotations

import asyncio

import pytest
from modgud import GuardClauseError

from tests import eop_fixtures as fx


class TestSemantics:
  """Elixir's ``cond``, as an expression."""

  @pytest.mark.parametrize(('x', 'expected'), [(-3, 'negative'), (0, 'zero'), (7, 'positive')])
  def test_first_true_clause_wins(self, x: int, expected: str) -> None:
    assert fx.sign(x) == expected

  @pytest.mark.parametrize(
    ('value', 'expected'),
    [(0, 'true'), ('', 'true'), ([], 'true'), (True, 'true'), (None, 'false'), (False, 'false')],
  )
  def test_only_none_and_false_are_false(self, value: object, expected: str) -> None:
    assert fx.elixir_truth(value) == expected

  def test_only_the_selected_test_and_value_run(self) -> None:
    fx.CALLS.clear()
    assert fx.lazy_cond(5) == 'small'
    assert fx.CALLS == ['t1', 't2', 'v2']

  def test_default_runs_only_when_nothing_matches(self) -> None:
    fx.CALLS.clear()
    assert fx.lazy_cond(-1) == 'none'
    assert fx.CALLS == ['t1', 't2', 'd']

  def test_a_raising_test_propagates(self) -> None:
    with pytest.raises(ZeroDivisionError):
      fx.cond_raising_test(0)

  def test_keyword_clause_arguments(self) -> None:
    assert fx.cond_keyword_clause(1) == 'pos'


class TestPositions:
  """An expression form works wherever an expression goes."""

  def test_nested_inside_a_clause_value(self) -> None:
    assert fx.nested_cond(1, 1) == 'both'
    assert fx.nested_cond(1, -1) == 'x only'
    assert fx.nested_cond(-1, 1) == 'neither'

  def test_comprehension_element(self) -> None:
    assert fx.cond_in_comprehension([1, 2, 3]) == ['odd', 'even', 'odd']

  def test_lambda_body(self) -> None:
    classify = fx.cond_in_lambda(10)
    assert (classify(11), classify(9)) == ('over', 'under')

  def test_while_test(self) -> None:
    assert fx.cond_in_while(3) == 3


class TestDecoratorsAndModes:
  """Both decorators, both modes, async and methods."""

  def test_under_guarded_expression(self) -> None:
    assert fx.guarded_cond(2) == 'pos'
    with pytest.raises(GuardClauseError):
      fx.guarded_cond(None)

  def test_explicit_return_mode_lowers_the_form(self) -> None:
    assert (fx.explicit_cond(2), fx.explicit_cond(-2)) == ('pos!', 'non-pos!')

  def test_explicit_return_mode_leaves_a_form_free_function_alone(self) -> None:
    assert fx.explicit_plain.__wrapped__.__code__.co_filename == fx.__file__  # type: ignore[attr-defined]
    assert fx.explicit_plain(1) == 2

  def test_async_function(self) -> None:
    assert asyncio.run(fx.async_cond(1)) == 'pos'

  def test_instance_method(self) -> None:
    assert fx.Shapes().sign(-1) == 'negative'
