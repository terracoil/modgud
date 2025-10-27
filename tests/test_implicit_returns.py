"""Tests for implicit return functionality."""

import pytest
from modgud.guarded_expression import guarded_expression
from modgud.guarded_expression.errors import ExplicitReturnDisallowedError, GuardClauseError

from tests.helpers import assert_guard_fails


def test_implicit_return_simple():
  """Basic implicit return without branching should work."""
  from tests.test_fixtures import calculate

  assert calculate() == 30


def test_implicit_return_with_if_else():
  """Implicit return should work with if/else branching."""
  from tests.test_fixtures import classify

  assert classify(5) == 'positive'
  assert classify(-5) == 'non-positive'
  assert classify(0) == 'non-positive'


def test_implicit_return_with_try_except():
  """Implicit return should work with try/except blocks."""
  from tests.test_fixtures import safe_divide

  assert safe_divide(10, 2) == 5.0
  assert safe_divide(10, 0) == 0


def test_implicit_return_disallows_explicit_return():
  """Explicit return should raise error when implicit_return=True."""
  with pytest.raises(ExplicitReturnDisallowedError):

    @guarded_expression(implicit_return=True, on_error=GuardClauseError)
    def bad_function():
      x = 10
      return x  # Should raise error


def test_combined_guard_and_implicit_return():
  """Guard validation should work with implicit return."""
  from tests.test_fixtures import safe_divide_with_guard

  assert safe_divide_with_guard(2) == 50.0
  assert_guard_fails(safe_divide_with_guard, -5, expected_message='Must be positive')


def test_common_guards_with_implicit_return():
  """CommonGuards should work with implicit return."""
  from tests.test_fixtures import double_with_guards

  assert double_with_guards(5) == 10

  with pytest.raises(GuardClauseError):
    double_with_guards(-5)
