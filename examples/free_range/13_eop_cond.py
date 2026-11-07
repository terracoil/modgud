"""``eop_cond``: Elixir's ``cond`` as an expression, usable wherever an expression goes.

Clauses are tested in order and only the chosen value is evaluated. As in Elixir, a test is
true unless it is ``None`` or ``False``, so ``0``, ``''`` and ``[]`` count as true. ``default=``
is required, so every call has a value.

Run: poetry run python examples/free_range/13_eop_cond.py
See: docs/api-reference.md#eop_cond
"""

from modgud import CommonGuards, eop_clause, eop_cond, guarded_expression, implicit_return


@implicit_return()
def sign(x: int) -> str:
  """Name the sign of ``x``; the tail expression is the return value."""
  eop_cond(
    eop_clause(x < 0, 'negative'),
    eop_clause(x == 0, 'zero'),
    default='positive',
  )


@guarded_expression(CommonGuards.not_none('items'))
def summary(items: list[str]) -> str:
  """Describe ``items``; only the chosen value runs, so ``items[0]`` is never touched when empty."""
  size: str = eop_cond(eop_clause(len(items) > 3, 'many'), eop_clause(items, 'few'), default='no')
  first: str = eop_cond(eop_clause(len(items) > 0, f'first={items[0]}'), default='first=none')
  f'{size} items, {first}'


@implicit_return()
def parities(values: list[int]) -> list[str]:
  """Use ``eop_cond`` inside a comprehension, which a statement never could."""
  [eop_cond(eop_clause(v % 2 == 0, 'even'), default='odd') for v in values]


@implicit_return()
def elixir_truth(value: object) -> str:
  """Show the Elixir rule: an empty list is true, ``None`` and ``False`` are not."""
  eop_cond(eop_clause(value, 'true'), default='false')


if __name__ == '__main__':
  assert [sign(-2), sign(0), sign(9)] == ['negative', 'zero', 'positive']
  assert summary(['a', 'b', 'c', 'd']) == 'many items, first=a'
  assert summary([]) == 'few items, first=none'  # [] is true under Elixir's rule
  assert parities([1, 2, 3]) == ['odd', 'even', 'odd']
  samples: list[object] = [[], 0, '', None, False]
  assert [elixir_truth(v) for v in samples] == ['true'] * 3 + ['false'] * 2

  print(f'sign: {sign(-2)}, {sign(0)}, {sign(9)}')
  print(f'summary([]) = {summary([])!r}')
