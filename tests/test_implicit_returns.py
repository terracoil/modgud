"""Tests for implicit return functionality."""

import pytest
from modgud import (
  ExplicitReturnDisallowedError,
  GuardClauseError,
  MissingImplicitReturnError,
  guarded_expression,
)

from tests.helpers import assert_guard_fails
from tests.test_fixtures import (
  calculate,
  calls_later_definition,
  clamp_to_limit,
  classify,
  describe_command,
  double_with_guards,
  safe_divide,
  safe_divide_with_guard,
)


class TestImplicitReturnBasics:
  """Tests for basic implicit return behavior without guards."""

  def test_implicit_return_simple(self):
    """Basic implicit return without branching should work."""
    assert calculate() == 30

  def test_implicit_return_with_if_else(self):
    """Implicit return should work with if/else branching."""
    assert classify(5) == 'positive'
    assert classify(-5) == 'non-positive'
    assert classify(0) == 'non-positive'

  def test_implicit_return_with_try_except(self):
    """Implicit return should work with try/except blocks."""
    assert safe_divide(10, 2) == 5.0
    assert safe_divide(10, 0) == 0

  def test_implicit_return_with_match_capture_tail(self):
    """A tail match ending in a bare capture yields a value on every path."""
    assert describe_command('go north') == 'going north'
    assert describe_command('exit') == 'bye'
    assert describe_command('dance wildly') == 'unknown: dance wildly'

  def test_implicit_return_refuses_match_without_wildcard(self):
    """A tail match that can fall through is refused at decoration time."""
    with pytest.raises(MissingImplicitReturnError, match='must end in a wildcard case'):

      @guarded_expression()
      def partial_match(x):
        match x:
          case 1:
            'one'

  def test_implicit_return_disallows_explicit_return(self):
    """Explicit return should raise error when implicit_return=True."""
    with pytest.raises(ExplicitReturnDisallowedError):

      @guarded_expression(implicit_return=True)
      def bad_function():
        x = 10
        return x  # Should raise error

  def test_implicit_return_disallows_return_in_nested_def(self):
    """A nested helper's ``return`` is refused too; the whole body is re-compiled as one unit."""
    with pytest.raises(ExplicitReturnDisallowedError):

      @guarded_expression()
      def with_nested_helper(x):
        def helper(y):
          return y + 1

        helper(x)


class TestImplicitReturnWithGuards:
  """Tests for implicit return combined with guard validation."""

  def test_combined_guard_and_implicit_return(self):
    """Guard validation should work with implicit return."""
    assert safe_divide_with_guard(2) == 50.0
    assert_guard_fails(safe_divide_with_guard, -5, expected_message='Must be positive')

  def test_common_guards_with_implicit_return(self):
    """Pre-built guards should work with implicit return."""
    assert double_with_guards(5) == 10

    with pytest.raises(GuardClauseError):
      double_with_guards(-5)


class TestLiveGlobals:
  def test_body_sees_names_defined_after_decoration(self):
    assert calls_later_definition() == 'late but present'

  def test_module_level_default_is_kept(self):
    assert clamp_to_limit() == 5
    assert clamp_to_limit(2) == 2
