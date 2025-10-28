"""Tests for built-in guard validators with various data types."""

import pytest
from modgud import (
  guarded_expression,
  in_range,
  matches_pattern,
  not_empty,
  not_none,
  positive,
  type_check,
)
from modgud.domain.models.errors import GuardClauseError


class TestCommonGuardValidation:
  """Tests for built-in guard validators with various data types."""

  @pytest.mark.parametrize(
    'guard_factory,valid_value,invalid_value,error_message',
    [
      (not_none('x'), 5, None, 'cannot be None'),
      (positive('x'), 5, -5, 'positive'),
      (not_empty('x'), 'hello', '', 'empty'),
      (type_check(int, 'x'), 5, '5', 'must be of type int'),
      (in_range(1, 10, 'x'), 5, 15, 'between 1 and 10'),
      (matches_pattern(r'^\d+$', 'x'), '123', 'abc', 'must match pattern'),
    ],
  )
  def test_common_guard_validation(self, guard_factory, valid_value, invalid_value, error_message):
    """Common guards should validate parameters correctly."""

    @guarded_expression(guard_factory, implicit_return=False)
    def process(x):
      return x * 2 if isinstance(x, (int, float)) else x + x

    # Valid value should pass
    result = process(valid_value)
    expected = (
      valid_value * 2 if isinstance(valid_value, (int, float)) else valid_value + valid_value
    )
    assert result == expected

    # Invalid value should fail with proper error message
    with pytest.raises(GuardClauseError) as exc_info:
      process(invalid_value)
    assert error_message in str(exc_info.value)
