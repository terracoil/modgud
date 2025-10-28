"""Tests for basic implicit return behavior without guards."""

import pytest
from modgud import guarded_expression
from modgud.domain.models.errors import ExplicitReturnDisallowedError, GuardClauseError


class TestImplicitReturnBasics:
  """Tests for basic implicit return behavior without guards."""

  def test_implicit_return_simple(self):
    """Basic implicit return without branching should work."""
    from tests.helpers import calculate

    assert calculate() == 30

  def test_implicit_return_with_if_else(self):
    """Implicit return should work with if/else branching."""
    from tests.helpers import classify

    assert classify(5) == 'positive'
    assert classify(-5) == 'non-positive'
    assert classify(0) == 'non-positive'

  def test_implicit_return_with_try_except(self):
    """Implicit return should work with try/except blocks."""
    from tests.helpers import safe_divide

    assert safe_divide(10, 2) == 5.0
    assert safe_divide(10, 0) == 0

  def test_implicit_return_disallows_explicit_return(self):
    """Explicit return should raise error when implicit_return=True."""
    with pytest.raises(ExplicitReturnDisallowedError):

      @guarded_expression(implicit_return=True, on_error=GuardClauseError)
      def bad_function():
        x = 10
        return x  # Should raise error
