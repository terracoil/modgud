"""Test decorator composition patterns with @implicit_return() and @guarded_expression.

Tests various composition patterns to ensure decorators work together correctly
without interference.
"""

import warnings

import pytest
from modgud import CommonGuards, GuardClauseError, guarded_expression, implicit_return


# Module-level functions for implicit return tests
@guarded_expression(CommonGuards.positive('x'))
@implicit_return()
def composed_guards_then_implicit(x):
  """Recommended composition: guards then implicit_return."""
  result = x * 2
  result  # noqa: B018 - implicit return


@implicit_return()
def standalone_implicit(x, y):
  """Standalone implicit return without guards."""
  if x > y:
    x + y
  else:
    x - y


@guarded_expression(CommonGuards.positive('x', position=0), CommonGuards.not_none('y', position=1))
def standalone_guards(x, y):
  """Standalone guards with implicit return (modern pattern)."""
  x + y


@guarded_expression(CommonGuards.positive('x'))
def guards_with_modern_pattern(x):
  """Guards with modern implicit return pattern."""
  x * 3


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

  @pytest.mark.parametrize('inner_rewrite', [False, True])
  def test_implicit_above_guards_refused(self, inner_rewrite):
    """``@implicit_return()`` above a guarded wrapper would re-compile the source and drop the
    guards, so it is refused at decoration time whether or not the inner layer rewrote.
    """
    with pytest.raises(TypeError, match=r'must sit below @guarded_expression'):

      @implicit_return()
      @guarded_expression(CommonGuards.positive('x'), implicit_return=inner_rewrite)
      def implicit_then_guards(x):
        x * 2

  def test_implicit_above_guarded_staticmethod_refused(self):
    """The marker is found through a ``staticmethod`` wrapper too."""
    with pytest.raises(TypeError, match=r'must sit below @guarded_expression'):
      implicit_return()(staticmethod(guarded_expression(implicit_return=False)(lambda x: x)))

  def test_guarded_wrapper_is_marked(self):
    """Every guarded wrapper carries the marker; a bare implicit-return function does not."""
    assert composed_guards_then_implicit.__modgud_guarded__ is True
    assert standalone_guards.__modgud_guarded__ is True
    assert not hasattr(standalone_implicit, '__modgud_guarded__')

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

  def test_no_deprecation_warning(self):
    """Test that no deprecation warning is issued for implicit_return parameter (feature undeprecated)."""
    with warnings.catch_warnings(record=True) as w:
      warnings.simplefilter('always')

      @guarded_expression(CommonGuards.positive('x'), implicit_return=False)
      def explicit_return_usage(x):
        return x * 2

      # Check that no deprecation warning was issued (feature is now supported)
      assert len(w) == 0

      # Verify functionality still works
      assert explicit_return_usage(5) == 10

  def test_no_warning_for_default(self):
    """Test that no warning is issued when using default implicit_return=True."""
    with warnings.catch_warnings(record=True) as w:
      warnings.simplefilter('always')

      @guarded_expression(CommonGuards.positive('x'))  # Default implicit_return=True
      def default_usage(x):
        result = x * 2
        result  # noqa: B018 - implicit return

      # No warning should be issued
      assert len(w) == 0

  def test_guards_with_modern_pattern(self):
    """Test guards with modern implicit return pattern."""
    result = guards_with_modern_pattern(3)
    assert result == 9


class TestMetadataPreservation:
  """Test that metadata is preserved through composition."""

  def test_function_name_preserved(self):
    """Test that __name__ is preserved."""
    assert composed_guards_then_implicit.__name__ == 'composed_guards_then_implicit'
    assert standalone_implicit.__name__ == 'standalone_implicit'
    assert guards_with_modern_pattern.__name__ == 'guards_with_modern_pattern'

  def test_docstring_preserved(self):
    """Test that __doc__ is preserved."""
    assert 'Recommended composition' in composed_guards_then_implicit.__doc__
    assert 'Standalone implicit' in standalone_implicit.__doc__
    assert 'Guards with modern' in guards_with_modern_pattern.__doc__

  def test_implicit_return_marker(self):
    """Test that implicit_return decorator adds marker attribute."""
    assert hasattr(standalone_implicit, '__implicit_return__')
    assert standalone_implicit.__implicit_return__ is True

    # Modern guards pattern still gets implicit_return behavior by default
    assert hasattr(guards_with_modern_pattern, '__implicit_return__')
