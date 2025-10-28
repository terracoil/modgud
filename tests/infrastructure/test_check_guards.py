"""Tests for guard validation logic."""

from modgud.infrastructure.adapters.guard_checker_adapter import GuardCheckerAdapter


class TestCheckGuards:
  """Tests for guard validation logic."""

  def test_check_guards_all_pass(self):
    """Test that check_guards returns None when all guards pass."""
    guards = (
      lambda x: x > 0 or 'Must be positive',
      lambda x: x < 100 or 'Must be less than 100',
    )
    result = GuardCheckerAdapter.check_guards(guards, (50,), {})
    assert result is None

  def test_check_guards_first_fails(self):
    """Test that check_guards returns error message from first failed guard."""
    guards = (
      lambda x: x > 0 or 'Must be positive',
      lambda x: x < 100 or 'Must be less than 100',
    )
    result = GuardCheckerAdapter.check_guards(guards, (-5,), {})
    assert result == 'Must be positive'

  def test_check_guards_second_fails(self):
    """Test that check_guards returns error message from second failed guard."""
    guards = (
      lambda x: x > 0 or 'Must be positive',
      lambda x: x < 100 or 'Must be less than 100',
    )
    result = GuardCheckerAdapter.check_guards(guards, (150,), {})
    assert result == 'Must be less than 100'

  def test_check_guards_boolean_false(self):
    """Test that check_guards handles boolean False guard result."""
    guards = (lambda x: False,)
    result = GuardCheckerAdapter.check_guards(guards, (5,), {})
    assert result == 'Guard clause failed'
