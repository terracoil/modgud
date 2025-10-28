"""Tests for GuardRegistry class."""

import pytest
from modgud import GuardRegistry


class TestGuardRegistry:
  """Tests for GuardRegistry class."""

  def test_register_and_get_global_guard(self):
    """Test registering and retrieving a guard in global namespace."""
    registry = GuardRegistry._create_for_testing()

    def sample_guard_factory(param_name: str = 'param'):
      def check(*args, **kwargs):
        return True

      return check

    registry._register('sample_guard', sample_guard_factory)
    retrieved = registry._get('sample_guard')

    assert retrieved is sample_guard_factory
    assert registry._has_guard('sample_guard')

  def test_register_and_get_namespaced_guard(self):
    """Test registering and retrieving a guard in a specific namespace."""
    registry = GuardRegistry._create_for_testing()

    def sample_guard_factory(param_name: str = 'param'):
      def check(*args, **kwargs):
        return True

      return check

    registry._register('sample_guard', sample_guard_factory, namespace='test_ns')
    retrieved = registry._get('sample_guard', namespace='test_ns')

    assert retrieved is sample_guard_factory
    assert registry._has_guard('sample_guard', namespace='test_ns')
    assert not registry._has_guard('sample_guard')  # Not in global namespace

  def test_duplicate_registration_error(self):
    """Test that registering the same guard twice raises an error."""
    registry = GuardRegistry._create_for_testing()

    def sample_guard_factory():
      def check(*args, **kwargs):
        return True

      return check

    registry._register('sample_guard', sample_guard_factory)

    with pytest.raises(ValueError, match='already registered'):
      registry._register('sample_guard', sample_guard_factory)

  def test_unregister_global_guard(self):
    """Test unregistering a global guard."""
    registry = GuardRegistry._create_for_testing()

    def guard():
      pass

    registry._register('guard1', guard)
    assert registry._has_guard('guard1')

    result = registry._unregister('guard1')
    assert result is True
    assert not registry._has_guard('guard1')
