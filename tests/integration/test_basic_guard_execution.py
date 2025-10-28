"""Tests for basic guard execution success and failure scenarios."""

from modgud import guarded_expression

from tests.helpers import assert_guard_fails


class TestBasicGuardExecution:
  """Tests for basic guard execution success and failure scenarios."""

  def test_basic_guard_success(self):
    """Guards should allow execution when predicates return True."""

    @guarded_expression(lambda x: x > 0 or 'Must be positive', implicit_return=False)
    def double(x):
      return x * 2

    assert double(5) == 10

  def test_basic_guard_failure_default_error(self):
    """GuardClauseError should be raised by default on guard failure."""

    @guarded_expression(lambda x: x > 0 or 'Must be positive', implicit_return=False)
    def double(x):
      return x * 2

    assert_guard_fails(double, -5, expected_message='Must be positive')
