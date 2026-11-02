"""Write your own guards, type a guard factory, and share it through GuardRegistry.

Run: poetry run python examples/free_range/07_custom_guards.py
See: docs/api-reference.md#guardregistry
"""

from typing import Any, Callable

from modgud import GuardClauseError, GuardFunction, GuardRegistry, guarded_expression


def fragile_ok(*args: Any, **kwargs: Any) -> bool | str:
  """Hand-written guard: refuse fragile parcels sent by sea (``mode`` is argument 1)."""
  mode: str = kwargs.get('mode', args[1] if len(args) > 1 else '')
  fragile: bool = kwargs.get('fragile', args[2] if len(args) > 2 else False)
  return not (fragile and mode == 'sea') or 'fragile parcels cannot go by sea'


def max_weight(limit: float, param_name: str = 'kg') -> GuardFunction:
  """Build a guard that refuses ``param_name`` (argument 0) above ``limit``."""

  def check(*args: Any, **kwargs: Any) -> bool | str:
    weight: float = kwargs.get(param_name, args[0] if args else 0.0)
    return weight <= limit or f'{param_name} must be at most {limit}'

  return check


GuardRegistry.register('max_weight', max_weight, namespace='shipping')
registered: Callable[..., GuardFunction] | None = GuardRegistry.get(
  'max_weight', namespace='shipping'
)
assert registered is not None  # get() returns None for unknown names


@guarded_expression(registered(30), fragile_ok)
def ship(kg: float, mode: str, fragile: bool = False) -> str:
  """Quote a shipment of ``kg`` kilograms by ``mode``."""
  f'{kg} kg by {mode}{" (fragile)" if fragile else ""}'


if __name__ == '__main__':
  assert ship(12, 'air', True) == '12 kg by air (fragile)'
  assert ship(kg=12, mode='sea') == '12 kg by sea'

  refusals: list[str] = []
  for kg, mode, fragile in [(40, 'air', False), (5, 'sea', True)]:
    try:
      ship(kg, mode, fragile)
    except GuardClauseError as error:
      refusals.append(str(error))
  assert refusals == ['kg must be at most 30', 'fragile parcels cannot go by sea']

  assert GuardRegistry.has_guard('max_weight', namespace='shipping')
  assert {'common', 'shipping'} <= set(GuardRegistry.list_namespaces())
  assert GuardRegistry.get('positive', namespace='common') is not None  # CommonGuards live here
  assert GuardRegistry.unregister('max_weight', namespace='shipping')
  assert not GuardRegistry.has_guard('max_weight', namespace='shipping')

  print(f'{ship(12, "air", True)}; refused: {refusals}')
