"""Every refusal of the ``eop_`` forms: malformed calls, misplaced calls and plain calls."""

from __future__ import annotations

from typing import Any

import pytest
from modgud import (
  MarkerNotRewrittenError,
  MarkerPlacementError,
  MarkerUsageError,
  eop_case,
  eop_clause,
  eop_cond,
  eop_match,
  eop_var,
  eop_when,
  implicit_return,
)

from tests.eop_fixtures import Point


class TestUsage:
  """A malformed form raises ``MarkerUsageError`` at decoration."""

  def test_missing_default(self) -> None:
    with pytest.raises(MarkerUsageError, match='needs default='):

      @implicit_return()
      def f(x: int) -> Any:
        eop_cond(eop_clause(x > 0, 'pos'))  # type: ignore[call-arg]

  def test_unknown_keyword(self) -> None:
    with pytest.raises(MarkerUsageError, match='accepts only default='):

      @implicit_return()
      def f(x: int) -> Any:
        eop_cond(eop_clause(x > 0, 'pos'), default=0, other=1)  # type: ignore[call-arg]

  def test_zero_clauses(self) -> None:
    with pytest.raises(MarkerUsageError, match='at least one eop_clause'):

      @implicit_return()
      def f(x: int) -> Any:
        eop_case(x, default=0)

  def test_missing_subject(self) -> None:
    with pytest.raises(MarkerUsageError, match='needs a subject'):

      @implicit_return()
      def f() -> Any:
        eop_case(default=0)  # type: ignore[call-arg]

  def test_clause_from_a_variable(self) -> None:
    with pytest.raises(MarkerUsageError, match='literal eop_clause'):

      @implicit_return()
      def f(x: int, clause: eop_clause[str]) -> Any:
        eop_cond(clause, default='no')

  def test_unpacked_clauses(self) -> None:
    with pytest.raises(MarkerUsageError, match='not unpacked'):

      @implicit_return()
      def f(clauses: list[eop_clause[str]]) -> Any:
        eop_cond(*clauses, default='no')

  def test_clause_with_three_parts(self) -> None:
    with pytest.raises(MarkerUsageError, match='exactly a test and a value'):

      @implicit_return()
      def f(x: int) -> Any:
        eop_cond(eop_clause(x > 0, 'pos', 'extra'), default='no')  # type: ignore[call-arg]

  def test_alternatives_are_not_patterns(self) -> None:
    with pytest.raises(MarkerUsageError, match='one clause per alternative'):

      @implicit_return()
      def f(x: object) -> Any:
        eop_case(x, eop_clause(Point(0, 0) | Point(1, 1), 'corner'), default='no')  # type: ignore[operator]

  def test_unsupported_pattern_node(self) -> None:
    with pytest.raises(MarkerUsageError, match='Lambda is not a supported pattern'):

      @implicit_return()
      def f(x: object) -> Any:
        eop_case(x, eop_clause(lambda: 1, 'callable'), default='no')

  def test_capture_bound_twice(self) -> None:
    with pytest.raises(MarkerUsageError, match='appears twice'):

      @implicit_return()
      def f(x: object) -> Any:
        eop_case(x, eop_clause(Point(eop_var.a, eop_var.a), 'same'), default='no')

  def test_two_stars(self) -> None:
    with pytest.raises(MarkerUsageError, match='only one star'):

      @implicit_return()
      def f(x: object) -> Any:
        eop_case(x, eop_clause([*eop_var.a, *eop_var.b], 'two'), default='no')

  def test_bare_name_as_mapping_key(self) -> None:
    with pytest.raises(MarkerUsageError, match='literal or a dotted name'):

      @implicit_return()
      def f(x: object, key: str) -> Any:
        eop_case(x, eop_clause({key: eop_var.v}, 'keyed'), default='no')

  def test_eop_match_arity(self) -> None:
    with pytest.raises(MarkerUsageError, match='exactly a pattern and a value'):

      @implicit_return()
      def f(x: object) -> Any:
        eop_match(Point(0, 0))  # type: ignore[call-arg]

  def test_eop_when_arity(self) -> None:
    with pytest.raises(MarkerUsageError, match='exactly a pattern and a guard'):

      @implicit_return()
      def f(x: object) -> Any:
        eop_match(eop_when(Point(0, eop_var.y)), x)  # type: ignore[call-arg]

  def test_walrus_in_a_guard(self) -> None:
    with pytest.raises(MarkerUsageError, match='cannot contain await, yield or :='):

      @implicit_return()
      def f(x: object) -> Any:
        eop_match(eop_when(eop_var.v, (n := eop_var.v) > 1), x)  # noqa: F841 - the walrus is the point

  def test_await_in_a_guard(self) -> None:
    with pytest.raises(MarkerUsageError, match='cannot contain await, yield or :='):

      @implicit_return()
      async def f(x: object) -> Any:
        eop_match(eop_when(eop_var.v, await eop_var.v), x)

  def test_capture_used_outside_its_clause(self) -> None:
    with pytest.raises(MarkerUsageError, match='usable only in the guard and value'):

      @implicit_return()
      def f(x: object) -> Any:
        eop_case(x, eop_clause(Point(eop_var.a, 0), 'a'), default=eop_var.a)

  def test_capture_used_in_eop_cond(self) -> None:
    with pytest.raises(MarkerUsageError, match='usable only in the guard and value'):

      @implicit_return()
      def f(x: int) -> Any:
        eop_cond(eop_clause(x > 0, eop_var.x), default=0)

  def test_marker_referenced_but_not_called(self) -> None:
    with pytest.raises(MarkerUsageError, match='referenced but never called'):

      @implicit_return()
      def f() -> Any:
        eop_cond  # noqa: B018 - the bare reference is the point

  def test_clause_outside_a_form(self) -> None:
    with pytest.raises(MarkerUsageError, match='belongs inside an eop_cond or eop_case'):

      @implicit_return()
      def f(x: int) -> Any:
        eop_clause(x > 0, 'alone')

  def test_when_outside_a_form(self) -> None:
    with pytest.raises(MarkerUsageError, match='belongs at the top of'):

      @implicit_return()
      def f(x: int) -> Any:
        eop_when(eop_var.v, True)

  def test_when_nested_inside_a_pattern(self) -> None:
    with pytest.raises(MarkerUsageError, match='cannot appear inside a pattern'):

      @implicit_return()
      def f(x: object) -> Any:
        eop_match(Point(eop_when(eop_var.v, True), 0), x)


class TestPlacement:
  """A well-formed form in a place it cannot go raises ``MarkerPlacementError``."""

  def test_guard_reading_a_comprehension_variable(self) -> None:
    with pytest.raises(MarkerPlacementError, match="cannot read 'limit'"):

      @implicit_return()
      def f(points: list[Point]) -> Any:
        [
          eop_match(eop_when(Point(eop_var.x, 0), eop_var.x > limit), p)
          for limit, p in enumerate(points)
        ]

  def test_bare_name_pattern_reading_a_lambda_parameter(self) -> None:
    with pytest.raises(MarkerPlacementError, match="cannot read 'n'"):

      @implicit_return()
      def f() -> Any:
        lambda n, v: eop_match(n, v)

  def test_eop_cond_in_a_comprehension_iterable(self) -> None:
    with pytest.raises(MarkerPlacementError, match="comprehension's first iterable"):

      @implicit_return()
      def f(flag: bool) -> Any:
        [v for v in eop_cond(eop_clause(flag, [1]), default=[])]

  def test_matcher_case_in_a_comprehension_iterable(self) -> None:
    with pytest.raises(MarkerPlacementError, match="comprehension's first iterable"):

      @implicit_return()
      def f(x: object) -> Any:
        [v for v in eop_case(x, eop_clause([eop_var.a], [eop_var.a]), default=[])]

  def test_inside_a_nested_class_body(self) -> None:
    with pytest.raises(MarkerPlacementError, match='class body'):

      @implicit_return()
      def f(x: int) -> Any:
        class Inner:
          label = eop_cond(eop_clause(x > 0, 'pos'), default='no')

        Inner  # noqa: B018 - implicit return


class TestPlainCalls:
  """Outside a decorated function every marker refuses with ``MarkerNotRewrittenError``."""

  @pytest.mark.parametrize(
    'call',
    [
      lambda: eop_cond(eop_clause(True, 1), default=0),
      lambda: eop_case(1, eop_clause(1, 'one'), default=0),
      lambda: eop_match(1, 1),
      lambda: eop_when(1, True),
      lambda: eop_var.anything,
    ],
    ids=['eop_cond', 'eop_case', 'eop_match', 'eop_when', 'eop_var'],
  )
  def test_each_marker_refuses(self, call: Any) -> None:
    with pytest.raises(MarkerNotRewrittenError, match='only works inside a function decorated'):
      call()

  def test_the_error_names_the_form(self) -> None:
    with pytest.raises(MarkerNotRewrittenError) as caught:
      eop_match(1, 1)
    assert caught.value.name == 'eop_match'

  def test_eop_var_keeps_dunder_lookups_honest(self) -> None:
    assert not hasattr(eop_var, '__wrapped__')

  def test_eop_clause_is_plain_data(self) -> None:
    clause = eop_clause(True, 'value')
    assert (clause.test, clause.value) == (True, 'value')
