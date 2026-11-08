"""Guards as static factory methods, the shape the house rules ask for, plus GuardRegistry.

Run: poetry run python examples/classy/07_custom_guards.py
See: docs/api-reference.md#guardregistry
"""

from typing import Any

from modgud import GuardClauseError, GuardFunction, GuardRegistry, guarded_expression


class ShippingGuards:
  """Shipping rules as guards, and one guarded quote that uses them."""

  @staticmethod
  def fragile_ok(*args: Any, **kwargs: Any) -> bool | str:
    """Hand-written guard: refuse fragile parcels sent by sea (``mode`` is argument 1)."""
    mode: str = kwargs.get('mode', args[1] if len(args) > 1 else '')
    fragile: bool = kwargs.get('fragile', args[2] if len(args) > 2 else False)
    return not (fragile and mode == 'sea') or 'fragile parcels cannot go by sea'

  @staticmethod
  def max_weight(limit: float, param_name: str = 'kg') -> GuardFunction:
    """Build a guard that refuses ``param_name`` (argument 0) above ``limit``."""

    def check(*args: Any, **kwargs: Any) -> bool | str:
      weight: float = kwargs.get(param_name, args[0] if args else 0.0)
      return weight <= limit or f'{param_name} must be at most {limit}'

    return check

  @staticmethod
  @guarded_expression(max_weight(30), fragile_ok)
  def quote(kg: float, mode: str, fragile: bool = False) -> str:
    """Quote a shipment of ``kg`` kilograms by ``mode``."""
    f'{kg} kg by {mode}{" (fragile)" if fragile else ""}'

  @classmethod
  def demo(cls) -> None:
    """Use the guards on a method, then share the factory through the registry."""
    assert cls.quote(12, 'air', True) == '12 kg by air (fragile)'
    refusals: list[str] = []
    for kg, mode, fragile in [(40, 'air', False), (5, 'sea', True)]:
      try:
        cls.quote(kg, mode, fragile)
      except GuardClauseError as error:
        refusals.append(str(error))
    assert refusals == ['kg must be at most 30', 'fragile parcels cannot go by sea']

    GuardRegistry.register('max_weight', cls.max_weight, namespace='shipping')
    assert GuardRegistry.has_guard('max_weight', namespace='shipping')
    assert {'common', 'shipping'} <= set(GuardRegistry.list_namespaces())
    factory: Any = GuardRegistry.get('max_weight', namespace='shipping')
    assert factory(5)(9) == 'kg must be at most 5'  # a guard is just a callable
    assert GuardRegistry.unregister('max_weight', namespace='shipping')
    assert not GuardRegistry.has_guard('max_weight', namespace='shipping')

    print(f'{cls.quote(12, "air", True)}; refused: {refusals}')


if __name__ == '__main__':
  ShippingGuards.demo()
