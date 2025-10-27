"""Integration tests for CommonGuards with guarded_expression decorator."""

import pytest
from modgud.guarded_expression import CommonGuards, guarded_expression
from modgud.guarded_expression.errors import GuardClauseError


@pytest.mark.parametrize(
  'guard_factory,valid_value,invalid_value,error_message',
  [
    (CommonGuards.not_none('x'), 5, None, 'cannot be None'),
    (CommonGuards.positive('x'), 5, -5, 'positive'),
    (CommonGuards.not_empty('x'), 'hello', '', 'empty'),
    (CommonGuards.type_check(int, 'x'), 5, '5', 'must be of type int'),
    (CommonGuards.in_range(1, 10, 'x'), 5, 15, 'between 1 and 10'),
    (CommonGuards.matches_pattern(r'^\d+$', 'x'), '123', 'abc', 'must match pattern'),
  ],
)
def test_common_guard_validation(guard_factory, valid_value, invalid_value, error_message):
  """Common guards should validate parameters correctly."""

  @guarded_expression(guard_factory, implicit_return=False)
  def process(x):
    return x * 2 if isinstance(x, (int, float)) else x + x

  # Valid value should pass
  result = process(valid_value)
  expected = valid_value * 2 if isinstance(valid_value, (int, float)) else valid_value + valid_value
  assert result == expected

  # Invalid value should fail with proper error message
  with pytest.raises(GuardClauseError) as exc_info:
    process(invalid_value)
  assert error_message in str(exc_info.value)


def test_common_guards_kwargs_precedence():
  """Named parameters should take precedence over positional mapping."""

  @guarded_expression(CommonGuards.positive('x'), implicit_return=False)
  def add(x, y):
    return x + y

  # Named parameter should work
  assert add(x=5, y=3) == 8

  # Should fail when named parameter is negative
  with pytest.raises(GuardClauseError) as exc_info:
    add(x=-5, y=3)
  assert 'positive' in str(exc_info.value)


def test_extract_param_out_of_bounds():
  """Guard should fail when parameter index is out of bounds and default is invalid."""

  @guarded_expression(CommonGuards.positive('y', 1), implicit_return=False)
  def single_param(x):
    return x * 2

  # Should fail because position 1 doesn't exist and default (0) is not positive
  with pytest.raises(GuardClauseError) as exc_info:
    single_param(5)
  assert 'positive' in str(exc_info.value)

  # Test with named parameter
  @guarded_expression(CommonGuards.positive('y'), implicit_return=False)
  def with_named(x, y=10):
    return x + y

  # Should work when y is positive
  assert with_named(5) == 15  # Uses default y=10
  assert with_named(5, y=20) == 25


def test_not_empty_with_object_lacking_len():
  """not_empty guard should handle objects without len() gracefully."""

  @guarded_expression(CommonGuards.not_empty('x'), implicit_return=False)
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
