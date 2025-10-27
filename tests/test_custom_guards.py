"""Tests for custom guard registration system."""

import pytest
from modgud import (
  get_guard,
  get_registry,
  guarded_expression,
  register_guard,
)
from modgud.guarded_expression.errors import GuardClauseError
from modgud.guarded_expression.guard_registry import GuardRegistry


class TestGuardRegistry:
  """Tests for GuardRegistry class."""

  def test_register_and_get_global_guard(self):
    """Test registering and retrieving a guard in global namespace."""
    registry = GuardRegistry()

    def sample_guard_factory(param_name: str = 'param'):
      def check(*args, **kwargs):
        result = True
        return result

      return check

    registry.register('sample_guard', sample_guard_factory)
    retrieved = registry.get('sample_guard')

    assert retrieved is sample_guard_factory
    assert registry.has_guard('sample_guard')

  def test_register_and_get_namespaced_guard(self):
    """Test registering and retrieving a guard in a specific namespace."""
    registry = GuardRegistry()

    def sample_guard_factory(param_name: str = 'param'):
      def check(*args, **kwargs):
        result = True
        return result

      return check

    registry.register('sample_guard', sample_guard_factory, namespace='test_ns')
    retrieved = registry.get('sample_guard', namespace='test_ns')

    assert retrieved is sample_guard_factory
    assert registry.has_guard('sample_guard', namespace='test_ns')
    assert not registry.has_guard('sample_guard')  # Not in global namespace

  def test_duplicate_registration_error(self):
    """Test that registering the same guard twice raises an error."""
    registry = GuardRegistry()

    def sample_guard_factory():
      def check(*args, **kwargs):
        result = True
        return result

      return check

    registry.register('sample_guard', sample_guard_factory)

    with pytest.raises(ValueError, match='already registered'):
      registry.register('sample_guard', sample_guard_factory)

  def test_unregister_global_guard(self):
    """Test unregistering a global guard."""
    registry = GuardRegistry()

    def guard():
      pass

    registry.register('guard1', guard)
    assert registry.has_guard('guard1')

    result = registry.unregister('guard1')
    assert result is True
    assert not registry.has_guard('guard1')


class TestGlobalRegistryFunctions:
  """Tests for global registry convenience functions."""

  def setup_method(self):
    """Clear global registry before each test."""
    registry = get_registry()
    for guard_name in list(registry.list_guards()):
      registry.unregister(guard_name)
    for namespace in list(registry.list_namespaces()):
      for guard_name in list(registry.list_guards(namespace=namespace)):
        registry.unregister(guard_name, namespace=namespace)

  def test_register_and_use_custom_guard(self):
    """Test registering and using a custom guard with guarded_expression."""

    def positive_number_factory(param_name: str = 'num', position: int = 0):
      def check(*args, **kwargs):
        value = args[position] if position < len(args) else kwargs.get(param_name)
        result = value > 0 or f'{param_name} must be positive'
        return result

      return check

    register_guard('positive_number', positive_number_factory, namespace='math')
    positive_guard = get_guard('positive_number', namespace='math')

    @guarded_expression(positive_guard('value'), implicit_return=False)
    def process_number(value: int):
      return value * 2

    result = process_number(5)
    assert result == 10

    with pytest.raises(GuardClauseError, match='value must be positive'):
      process_number(-5)
