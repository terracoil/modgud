"""Tests for basic guard clause functionality."""

import pytest
from modgud.expression_oriented import guarded_expression

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


class TestGuardFailureHandling:
  """Tests for different guard failure handling strategies."""

  def test_guard_failure_custom_return_value(self):
    """Custom value should be returned on guard failure when configured."""

    @guarded_expression(
      lambda x: x > 0 or 'Must be positive',
      on_error={'error': 'Invalid input'},
      implicit_return=False,
    )
    def double(x):
      return x * 2

    assert double(-5) == {'error': 'Invalid input'}

  def test_guard_failure_custom_exception(self):
    """Custom exception should be raised on guard failure when configured."""

    @guarded_expression(
      lambda x: x > 0 or 'Must be positive', on_error=ValueError, implicit_return=False
    )
    def double(x):
      return x * 2

    with pytest.raises(ValueError) as exc_info:
      double(-5)
    assert 'Must be positive' in str(exc_info.value)

  def test_guard_failure_custom_handler(self):
    """Custom handler should process guard failures when configured."""

    def custom_handler(error_msg, *args, **kwargs):
      result = f'Handled: {error_msg}'
      return result

    @guarded_expression(
      lambda x: x > 0 or 'Must be positive',
      on_error=custom_handler,
      implicit_return=False,
    )
    def double(x):
      return x * 2

    assert double(-5) == 'Handled: Must be positive'


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
