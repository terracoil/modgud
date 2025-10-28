"""Tests for edge cases in implicit return transformation."""

import pytest


class TestImplicitReturnEdgeCases:
  """Tests for edge cases in implicit return transformation."""

  def test_noop_function_with_pass(self):
    """Function with only pass should handle gracefully."""
    from tests.helpers import noop_function

    # pass statement should result in None being returned
    result = noop_function(5)
    assert result is None

  def test_exception_only_function(self):
    """Function that only raises exceptions should work correctly."""
    from tests.helpers import exception_only_function

    # All paths raise exceptions
    with pytest.raises(ValueError, match='Negative value'):
      exception_only_function(-5)

    with pytest.raises(RuntimeError, match='Non-negative value'):
      exception_only_function(5)

  def test_empty_function_body(self):
    """Function with just docstring should handle gracefully."""
    from tests.helpers import empty_function

    # Empty body should result in None being returned
    result = empty_function(10)
    assert result is None

  def test_conditional_noop_paths(self):
    """Function with some paths having values and some having pass."""
    from tests.helpers import conditional_noop

    # Positive path has value
    assert conditional_noop(5) == 10

    # Negative path has pass (should return None)
    result = conditional_noop(-5)
    assert result is None

    # Zero path has None (should return None)
    result = conditional_noop(0)
    assert result is None
