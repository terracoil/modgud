"""Tests for decorator behavior when no guards are provided."""

from modgud import guarded_expression
from modgud.domain.models.errors import GuardClauseError


class TestDecoratorWithoutGuards:
  """Tests for decorator behavior when no guards are provided."""

  def test_no_guards_implicit_return_false(self):
    """Decorator should work with no guards and implicit_return=False."""

    @guarded_expression(implicit_return=False, on_error=GuardClauseError)
    def simple(x):
      return x * 2

    assert simple(5) == 10

  def test_no_guards_implicit_return_true(self):
    """Decorator should work with no guards and implicit_return=True."""
    from tests.helpers import simple_implicit

    assert simple_implicit(5) == 10
