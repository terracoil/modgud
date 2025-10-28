"""Tests for multiple guard clause execution and failure modes."""

from modgud import guarded_expression

from tests.helpers import assert_guard_fails


class TestMultipleGuards:
  """Tests for multiple guard clause execution and failure modes."""

  def test_multiple_guards_all_pass(self):
    """All guards must pass for function to execute."""

    @guarded_expression(
      lambda x: x > 0 or 'Must be positive',
      lambda x: x < 100 or 'Must be less than 100',
      implicit_return=False,
    )
    def double(x):
      return x * 2

    assert double(50) == 100

  def test_multiple_guards_first_fails(self):
    """First guard failure should stop evaluation immediately."""

    @guarded_expression(
      lambda x: x > 0 or 'Must be positive',
      lambda x: x < 100 or 'Must be less than 100',
      implicit_return=False,
    )
    def double(x):
      return x * 2

    assert_guard_fails(double, -5, expected_message='Must be positive')

  def test_multiple_guards_second_fails(self):
    """Second guard failure should be caught after first passes."""

    @guarded_expression(
      lambda x: x > 0 or 'Must be positive',
      lambda x: x < 100 or 'Must be less than 100',
      implicit_return=False,
    )
    def double(x):
      return x * 2

    assert_guard_fails(double, 150, expected_message='Must be less than 100')
