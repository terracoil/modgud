"""``eop_match`` end to end: patterns, guards, privacy and positions."""

from __future__ import annotations

from tests import eop_fixtures as fx
from tests.eop_fixtures import Circle, Point


class TestMatching:
  """Elixir's ``match?``, returning a real ``bool``."""

  def test_class_pattern_with_wildcard(self) -> None:
    assert fx.is_on_y_axis(Point(0, 9)) is True
    assert fx.is_on_y_axis(Point(1, 9)) is False
    assert fx.is_on_y_axis(Circle(1)) is False
    assert fx.is_on_y_axis('not a shape') is False

  def test_guarded_pattern(self) -> None:
    assert fx.is_above_origin(Point(0, 2)) is True
    assert fx.is_above_origin(Point(0, -2)) is False

  def test_a_guard_must_be_exactly_true(self) -> None:
    assert fx.guard_truthy_only(True) is True
    assert fx.guard_truthy_only(1) is False
    assert fx.guard_truthy_only([1]) is False

  def test_a_raising_guard_is_no_match(self) -> None:
    assert fx.guard_raises(3) is False

  def test_a_bare_name_compares_by_value(self) -> None:
    assert fx.match_bare_name(5) is True
    assert fx.match_bare_name(6) is False

  def test_a_guard_reads_the_functions_locals(self) -> None:
    assert fx.match_reads_local_in_guard(5, 4) is True
    assert fx.match_reads_local_in_guard(5, 6) is False


class TestScopeAndPositions:
  """Captures stay private, and the form fits anywhere."""

  def test_captures_do_not_leak(self) -> None:
    assert fx.match_captures_do_not_leak(Point(0, 7)) == 'untouched'

  def test_comprehension_filter(self) -> None:
    shapes: list[object] = [Point(0, 1), Point(1, 1), Circle(2), Point(0, 3)]
    assert fx.filter_on_axis(shapes) == [Point(0, 1), Point(0, 3)]

  def test_first_iterable_of_a_comprehension(self) -> None:
    assert fx.match_in_first_iterable([Point(0, 1), Point(1, 1)]) == [True, False]

  def test_static_method(self) -> None:
    assert fx.Shapes.is_origin(Point(0, 0)) is True
    assert fx.Shapes.is_origin(Point(0, 1)) is False
