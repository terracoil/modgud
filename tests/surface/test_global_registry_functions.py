"""Tests for global registry convenience functions."""

import pytest
from modgud import GuardRegistry, guarded_expression
from modgud.domain.models.errors import GuardClauseError


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
