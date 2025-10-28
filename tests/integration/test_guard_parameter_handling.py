"""Tests for guard parameter extraction and precedence."""

import pytest
from modgud import guarded_expression, not_empty, positive
from modgud.domain.models.errors import GuardClauseError


class TestGuardParameterHandling:
  """Tests for guard parameter extraction and precedence."""

  def test_common_guards_kwargs_precedence(self):
    """Named parameters should take precedence over positional mapping."""

    @guarded_expression(positive('x'), implicit_return=False)
    def add(x, y):
      return x + y

    # Named parameter should work
    assert add(x=5, y=3) == 8

    # Should fail when named parameter is negative
    with pytest.raises(GuardClauseError) as exc_info:
      add(x=-5, y=3)
    assert 'positive' in str(exc_info.value)

  def test_extract_param_out_of_bounds(self):
    """Guard should fail when parameter index is out of bounds and default is invalid."""

    @guarded_expression(positive('y', 1), implicit_return=False)
    def single_param(x):
      return x * 2

    # Should fail because position 1 doesn't exist and default (0) is not positive
    with pytest.raises(GuardClauseError) as exc_info:
      single_param(5)
    assert 'positive' in str(exc_info.value)

    # Test with named parameter
    @guarded_expression(positive('y'), implicit_return=False)
    def with_named(x, y=10):
      return x + y

    # Should work when y is positive
    assert with_named(5) == 15  # Uses default y=10
    assert with_named(5, y=20) == 25

  def test_not_empty_with_object_lacking_len(self):
    """not_empty guard should handle objects without len() gracefully."""

    @guarded_expression(not_empty('x'), implicit_return=False)
    def process(x):
      return str(x)

    # Should work with strings and lists
    assert process('hello') == 'hello'
    assert process([1, 2]) == '[1, 2]'

    # Should fail for empty containers
    with pytest.raises(GuardClauseError) as exc_info:
      process('')
    assert 'empty' in str(exc_info.value)

    # Should pass for truthy objects without len()
    assert process(42) == '42'  # Numbers don't have len(), but bool(42) is True

    # Should fail for falsy objects without len()
    with pytest.raises(GuardClauseError) as exc_info:
      process(None)  # None is falsy, so fails not_empty check
    assert 'empty' in str(exc_info.value)
