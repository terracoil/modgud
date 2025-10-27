"""Tests for basic guard clause functionality."""

import pytest
from modgud.guarded_expression import guarded_expression

from tests.helpers import assert_guard_fails


def test_basic_guard_success():
  """Guards should allow execution when predicates return True."""

  @guarded_expression(lambda x: x > 0 or 'Must be positive', implicit_return=False)
  def double(x):
    return x * 2

  assert double(5) == 10


def test_basic_guard_failure_default_error():
  """GuardClauseError should be raised by default on guard failure."""

  @guarded_expression(lambda x: x > 0 or 'Must be positive', implicit_return=False)
  def double(x):
    return x * 2

  assert_guard_fails(double, -5, expected_message='Must be positive')


def test_guard_failure_custom_return_value():
  """Custom value should be returned on guard failure when configured."""

  @guarded_expression(
    lambda x: x > 0 or 'Must be positive',
    on_error={'error': 'Invalid input'},
    implicit_return=False,
  )
  def double(x):
    return x * 2

  assert double(-5) == {'error': 'Invalid input'}


def test_guard_failure_custom_exception():
  """Custom exception should be raised on guard failure when configured."""

  @guarded_expression(
    lambda x: x > 0 or 'Must be positive', on_error=ValueError, implicit_return=False
  )
  def double(x):
    return x * 2

  with pytest.raises(ValueError) as exc_info:
    double(-5)
  assert 'Must be positive' in str(exc_info.value)


def test_guard_failure_custom_handler():
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


def test_multiple_guards_all_pass():
  """All guards must pass for function to execute."""

  @guarded_expression(
    lambda x: x > 0 or 'Must be positive',
    lambda x: x < 100 or 'Must be less than 100',
    implicit_return=False,
  )
  def double(x):
    return x * 2

  assert double(50) == 100


def test_multiple_guards_first_fails():
  """First guard failure should stop evaluation immediately."""

  @guarded_expression(
    lambda x: x > 0 or 'Must be positive',
    lambda x: x < 100 or 'Must be less than 100',
    implicit_return=False,
  )
  def double(x):
    return x * 2

  assert_guard_fails(double, -5, expected_message='Must be positive')


def test_multiple_guards_second_fails():
  """Second guard failure should be caught after first passes."""

  @guarded_expression(
    lambda x: x > 0 or 'Must be positive',
    lambda x: x < 100 or 'Must be less than 100',
    implicit_return=False,
  )
  def double(x):
    return x * 2

  assert_guard_fails(double, 150, expected_message='Must be less than 100')
