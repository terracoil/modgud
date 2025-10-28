"""Tests for implicit return combined with guard validation."""

import pytest
from modgud.domain.models.errors import GuardClauseError

from tests.helpers import assert_guard_fails


class TestImplicitReturnWithGuards:
  """Tests for implicit return combined with guard validation."""

  def test_combined_guard_and_implicit_return(self):
    """Guard validation should work with implicit return."""
    from tests.helpers import safe_divide_with_guard

    assert safe_divide_with_guard(2) == 50.0
    assert_guard_fails(safe_divide_with_guard, -5, expected_message='Must be positive')

  def test_common_guards_with_implicit_return(self):
    """Pre-built guards should work with implicit return."""
    from tests.helpers import double_with_guards

    assert double_with_guards(5) == 10

    with pytest.raises(GuardClauseError):
      double_with_guards(-5)
