"""Tests for custom guard registration system."""

import pytest
from modgud import GuardRegistry, guarded_expression
from modgud.expression_oriented.core.errors import GuardClauseError


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


class TestGlobalRegistryFunctions:
  """Tests for global registry convenience functions."""

  def setup_method(self):
    """Clear global registry before each test."""
    registry = GuardRegistry.instance()
    for guard_name in list(registry._list_guards()):
      registry._unregister(guard_name)
    for namespace in list(registry._list_namespaces()):
      for guard_name in list(registry._list_guards(namespace=namespace)):
        registry._unregister(guard_name, namespace=namespace)

  def test_register_and_use_custom_guard(self):
    """Test registering and using a custom guard with guarded_expression."""

    def positive_number_factory(param_name: str = 'num', position: int = 0):
      def check(*args, **kwargs):
        value = args[position] if position < len(args) else kwargs.get(param_name)
        result = value > 0 or f'{param_name} must be positive'
        return result

      return check

    GuardRegistry.register('positive_number', positive_number_factory, namespace='math')
    positive_guard = GuardRegistry.get('positive_number', namespace='math')

    @guarded_expression(positive_guard('value'), implicit_return=False)
    def process_number(value: int):
      return value * 2

    result = process_number(5)
    assert result == 10

    with pytest.raises(GuardClauseError, match='value must be positive'):
      process_number(-5)
