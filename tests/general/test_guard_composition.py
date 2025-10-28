"""Tests for guard function composition and chaining."""

import pytest
from modgud import guarded_expression
from modgud.domain.models.errors import GuardClauseError


class TestGuardComposition:
  """Tests for guard function composition and chaining."""

  def test_composed_guards(self):
    """Multiple validation layers should compose correctly."""

    def create_validation_layer(layer_name: str):
      def guard(*args, **kwargs):
        # Pass through - just for composition testing
        return True

      return guard

    @guarded_expression(
      create_validation_layer('auth'),
      create_validation_layer('permissions'),
      create_validation_layer('rate_limit'),
      create_validation_layer('input_validation'),
      implicit_return=False,
    )
    def api_endpoint(data):
      return {'status': 'ok', 'data': data}

    assert api_endpoint('test') == {'status': 'ok', 'data': 'test'}

  def test_guard_short_circuit(self):
    """Guards should short-circuit on first failure."""
    call_count = {'guard1': 0, 'guard2': 0, 'guard3': 0}

    def counting_guard1(*args, **kwargs):
      call_count['guard1'] += 1
      return False or 'Guard 1 failed'

    def counting_guard2(*args, **kwargs):
      call_count['guard2'] += 1
      return True

    def counting_guard3(*args, **kwargs):
      call_count['guard3'] += 1
      return True

    @guarded_expression(counting_guard1, counting_guard2, counting_guard3, implicit_return=False)
    def process(x):
      return x

    with pytest.raises(GuardClauseError):
      process(5)

    # Only first guard should have been called due to short-circuit
    assert call_count['guard1'] == 1
    assert call_count['guard2'] == 0
    assert call_count['guard3'] == 0
