"""Tests for different guard failure handling strategies."""

import pytest
from modgud import guarded_expression


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
