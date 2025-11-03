"""
Test decorator composition patterns with @implicit_return and @guarded_expression.

Tests various composition patterns to ensure decorators work together correctly
without interference.
"""

import warnings

import pytest
from modgud import GuardClauseError, guarded_expression, implicit_return, not_none, positive


# Module-level functions for implicit return tests
@guarded_expression(positive('x'))
@implicit_return
def composed_guards_then_implicit(x):
  """Recommended composition: guards then implicit_return."""
  result = x * 2
  result


# This composition pattern is dangerous because it bypasses guards!
# When @implicit_return wraps a guarded function, it re-transforms the original
# source, effectively removing the guard wrapper
@implicit_return
@guarded_expression(positive('x'), implicit_return=False)
def composed_implicit_then_guards(x):
  """Invalid composition: bypasses guards due to source retrieval behavior."""
  result = x * 2
  result


@implicit_return
def standalone_implicit(x, y):
  """Standalone implicit return without guards."""
  if x > y:
    x + y
  else:
    x - y


@guarded_expression(positive('x', position=0), not_none('y', position=1), implicit_return=False)
def standalone_guards(x, y):
  """Standalone guards without implicit return."""
  return x + y


@guarded_expression(positive('x'), implicit_return=False)
def guards_with_explicit_false(x):
  """Guards with explicit implicit_return=False."""
  return x * 3


class TestDecoratorComposition:
  """Test various decorator composition patterns."""

  def test_guards_then_implicit_success(self):
    """Test recommended composition order with valid input."""
    result = composed_guards_then_implicit(5)
    assert result == 10

  def test_guards_then_implicit_failure(self):
    """Test recommended composition order with invalid input."""
    with pytest.raises(GuardClauseError, match='x must be positive'):
      composed_guards_then_implicit(-5)

  def test_implicit_then_guards_bypasses_guards(self):
    """Test that implicit_return wrapping guards bypasses the guards (BUG)."""
    # This is a known issue: when @implicit_return wraps a guarded function,
    # it re-transforms the original source, bypassing the guard wrapper
    result = composed_implicit_then_guards(5)
    assert result == 10

    # This should raise GuardClauseError but doesn't due to the bug
    result = composed_implicit_then_guards(-5)
    assert result == -10  # Guards are bypassed!

  def test_standalone_implicit(self):
    """Test standalone implicit_return decorator."""
    assert standalone_implicit(10, 5) == 15
    assert standalone_implicit(5, 10) == -5

  def test_standalone_guards(self):
    """Test standalone guards without implicit return."""
    assert standalone_guards(5, 10) == 15
    with pytest.raises(GuardClauseError, match='x must be positive'):
      standalone_guards(-5, 10)
    with pytest.raises(GuardClauseError, match='y cannot be None'):
      standalone_guards(5, None)

  def test_deprecation_warning(self):
    """Test that deprecation warning is issued for implicit_return parameter."""
    with warnings.catch_warnings(record=True) as w:
      warnings.simplefilter('always')

      @guarded_expression(positive('x'), implicit_return=False)
      def deprecated_usage(x):
        return x * 2

      # Check that a deprecation warning was issued
      assert len(w) == 1
      assert issubclass(w[0].category, DeprecationWarning)
      assert "implicit_return' parameter on @guarded_expression is deprecated" in str(w[0].message)
      assert 'Use the @implicit_return decorator separately' in str(w[0].message)

  def test_no_warning_for_default(self):
    """Test that no warning is issued when using default implicit_return=True."""
    with warnings.catch_warnings(record=True) as w:
      warnings.simplefilter('always')

      @guarded_expression(positive('x'))  # Default implicit_return=True
      def default_usage(x):
        result = x * 2
        result

      # No warning should be issued
      assert len(w) == 0

  def test_guards_with_explicit_false(self):
    """Test guards with explicit implicit_return=False."""
    # The deprecation warning is issued when the decorator is created (at module import),
    # not when the function is called
    result = guards_with_explicit_false(3)
    assert result == 9


class TestMetadataPreservation:
  """Test that metadata is preserved through composition."""

  def test_function_name_preserved(self):
    """Test that __name__ is preserved."""
    assert composed_implicit_then_guards.__name__ == 'composed_implicit_then_guards'
    assert composed_guards_then_implicit.__name__ == 'composed_guards_then_implicit'
    assert standalone_implicit.__name__ == 'standalone_implicit'
    assert standalone_guards.__name__ == 'standalone_guards'

  def test_docstring_preserved(self):
    """Test that __doc__ is preserved."""
    assert 'Recommended composition' in composed_guards_then_implicit.__doc__
    assert 'Invalid composition' in composed_implicit_then_guards.__doc__
    assert 'Standalone implicit' in standalone_implicit.__doc__
    assert 'Standalone guards' in standalone_guards.__doc__

  def test_implicit_return_marker(self):
    """Test that implicit_return decorator adds marker attribute."""
    assert hasattr(standalone_implicit, '__implicit_return__')
    assert standalone_implicit.__implicit_return__ is True

    # Guards-only function should not have the marker
    assert not hasattr(standalone_guards, '__implicit_return__')
