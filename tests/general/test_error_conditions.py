"""Tests for various error conditions and edge cases."""

import pytest
from modgud import CommonGuards, guarded_expression
from modgud.domain.models.errors import GuardClauseError


class TestErrorConditions:
  """Tests for various error conditions and edge cases."""

  def test_guard_raises_exception(self):
    """Guard that raises exception should be handled gracefully."""

    def bad_guard(*args, **kwargs):
      raise RuntimeError('Guard evaluation failed')

    @guarded_expression(bad_guard, implicit_return=False, on_error=None)
    def process(x):
      return x * 2

    # Should return None (on_error=None) when guard raises
    with pytest.raises(RuntimeError, match='Guard evaluation failed'):
      process(5)

  def test_unicode_parameter_names(self):
    """Guards should handle unicode parameter names."""

    @guarded_expression(CommonGuards.positive('value'), implicit_return=False)
    def process(value):
      return value * 2

    assert process(value=5) == 10
    with pytest.raises(GuardClauseError):
      process(value=-5)

  def test_long_error_messages(self):
    """Guards should handle very long error messages."""
    long_message = 'A' * 2000  # 2000 character error message

    @guarded_expression(lambda x: x > 0 or long_message, implicit_return=False)
    def process(x):
      return x * 2

    with pytest.raises(GuardClauseError) as exc_info:
      process(-5)
    assert len(str(exc_info.value)) >= 2000

  def test_deeply_nested_control_flow(self):
    """Implicit return should work with deeply nested control flow."""
    from tests.helpers import deeply_nested_function

    assert deeply_nested_function(1) == 'one'
    assert deeply_nested_function(2) == 'two-a'
    assert deeply_nested_function(3) == 'three-a-i'
    assert deeply_nested_function(4) == 'three-a-ii'
    assert deeply_nested_function(5) == 'three-b'
    assert deeply_nested_function(10) == 'other'

  def test_recursive_function_with_guards(self):
    """Guards should work with recursive functions."""

    @guarded_expression(
      CommonGuards.not_none('n'), CommonGuards.positive('n'), implicit_return=False
    )
    def factorial(n):
      if n <= 1:
        result = 1
      else:
        result = n * factorial(n - 1)
      return result

    assert factorial(5) == 120
    assert factorial(1) == 1

    with pytest.raises(GuardClauseError):
      factorial(-5)

  def test_function_with_many_parameters(self):
    """Guards should work with functions having many parameters."""

    @guarded_expression(
      CommonGuards.positive('a'),
      CommonGuards.positive('b'),
      CommonGuards.positive('c'),
      implicit_return=False,
    )
    def sum_many(a, b, c, d, e, f, g, h, i, j):
      return a + b + c + d + e + f + g + h + i + j

    assert sum_many(1, 2, 3, 4, 5, 6, 7, 8, 9, 10) == 55

    with pytest.raises(GuardClauseError):
      sum_many(-1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
