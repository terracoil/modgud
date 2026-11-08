"""``eop_case`` end to end on both lowering paths, against handwritten ``match`` oracles."""

from __future__ import annotations

import asyncio
from collections import deque
from typing import Any

import pytest

from tests import eop_fixtures as fx
from tests.eop_fixtures import Circle, Color, Point

SUBJECTS: list[Any] = [
  Point(0, 2),
  Point(0, -2),
  Point(0, 0),
  Point(3, 0),
  Point(3, 4),
  Circle(1),
  [],
  [7],
  [7, 8, 9],
  (7, 8),
  'text',
  b'bytes',
  {'id': 1, 'k': 2},
  {'k': 2},
  {},
  0,
  0.0,
  -1,
  1,
  True,
  False,
  None,
  5,
  Color.RED,
  Color.BLUE,
  [Point(1, 2), Point(3, 4)],
  [Point(1, 2)],
  float('nan'),
  deque([1]),
  object(),
]


class TestDifferential:
  """Both paths agree with a real ``match`` on every subject."""

  @pytest.mark.parametrize('subject', SUBJECTS, ids=repr)
  def test_describe_hoisted(self, subject: Any) -> None:
    assert fx.describe(subject) == fx.oracle_describe(subject)

  def test_describe_matchers(self) -> None:
    assert fx.describe_all(SUBJECTS) == [fx.oracle_describe(s) for s in SUBJECTS]

  @pytest.mark.parametrize('subject', SUBJECTS, ids=repr)
  def test_sequence_patterns(self, subject: Any) -> None:
    assert fx.case_sequence(subject) == fx.oracle_sequence(subject)

  @pytest.mark.parametrize('subject', SUBJECTS, ids=repr)
  def test_mapping_patterns(self, subject: Any) -> None:
    assert fx.case_mapping(subject) == fx.oracle_mapping(subject)

  @pytest.mark.parametrize('subject', SUBJECTS, ids=repr)
  def test_value_patterns_hoisted(self, subject: Any) -> None:
    assert fx.case_values(subject) == fx.oracle_values(subject)

  def test_value_patterns_matchers(self) -> None:
    assert fx.case_values_matchers(SUBJECTS) == [fx.oracle_values(s) for s in SUBJECTS]

  @pytest.mark.parametrize('subject', SUBJECTS, ids=repr)
  def test_keyword_and_nested_class_patterns(self, subject: Any) -> None:
    assert fx.case_keyword_class(subject) == fx.oracle_keyword_class(subject)


class TestEvaluation:
  """Subject once, selected value only, default lazy, captures private."""

  def test_hoisted_path_is_lazy(self) -> None:
    fx.CALLS.clear()
    assert fx.lazy_case(2) == 'two'
    assert fx.CALLS == ['subject', 'v2']

  def test_hoisted_default_runs_only_on_miss(self) -> None:
    fx.CALLS.clear()
    assert fx.lazy_case(9) == 'other'
    assert fx.CALLS == ['subject', 'd']

  def test_matcher_path_is_lazy(self) -> None:
    fx.CALLS.clear()
    assert fx.lazy_case_matchers([1, 9]) == ['one', 'other']
    assert fx.CALLS == ['subject', 'v1', 'subject', 'd']

  def test_matcher_path_evaluates_the_subject_once(self) -> None:
    values: deque[int] = deque([2, 99])
    assert fx.case_subject_once(values) == 'two!'
    assert list(values) == [99]

  def test_captures_are_private(self) -> None:
    assert fx.case_captures_private(Point(0, 1)) == ('axis', 'untouched')

  @pytest.mark.parametrize(
    ('value', 'expected'),
    [(True, 'truthy'), (1, 'fell through'), (3, 'three'), ([1], 'fell through')],
  )
  def test_guard_rules_hoisted(self, value: object, expected: str) -> None:
    assert fx.case_guard_rules(value) == expected

  def test_guard_rules_matchers(self) -> None:
    assert fx.case_guard_rules_matchers([True, 1, 3, [1]]) == [
      'truthy',
      'fell through',
      'three',
      'fell through',
    ]


class TestPositions:
  """Hoisted where the call is a whole value, matchers elsewhere."""

  def test_assigned(self) -> None:
    assert fx.describe_assigned(Point(1, 1)) == '<point>'
    assert fx.describe_assigned(3) == '<other>'

  def test_operand(self) -> None:
    assert fx.case_in_operand(Point(4, 0)) == 'shape: x=4'

  def test_nested_forms(self) -> None:
    assert fx.case_nested_forms(Point(2, 2)) == 'diagonal'
    assert fx.case_nested_forms(Point(2, 3)) == 'off diagonal'
    assert fx.case_nested_forms(None) == 'diagonal'
    assert fx.case_nested_forms('x') == 'not a point'

  def test_inside_a_branch(self) -> None:
    assert fx.case_in_branch(True, Point(6, 0)) == 'x 6'
    assert fx.case_in_branch(False, Point(6, 0)) == 'skipped'

  def test_async(self) -> None:
    assert asyncio.run(fx.async_case(Point(8, 0))) == 'got 8'

  def test_class_method(self) -> None:
    assert fx.Shapes.describe(Point(1, 2)) == '1,2'

  def test_explicit_return_mode(self) -> None:
    assert fx.explicit_case(Point(3, 3)) == 'X=3'
