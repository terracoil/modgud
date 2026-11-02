"""Standalone @implicit_return(): if/elif/else, try/except/else and match/case tails.

Run: poetry run python examples/free_range/04_implicit_returns.py
See: docs/api-reference.md#implicit_return
"""

from modgud import implicit_return


@implicit_return()
def grade(score: int) -> str:
  """Map ``score`` to a letter; every branch ends in the value it yields."""
  if score >= 90:
    'A'
  elif score >= 75:
    'B'
  else:
    'C'


@implicit_return()
def to_cents(text: str) -> int:
  """Parse ``text`` as an amount in dollars and return cents, or 0 if it isn't a number."""
  try:
    dollars: float = float(text)
    dollars  # noqa: B018 - the try body needs a tail; the else branch replaces it on success
  except ValueError:
    0  # noqa: B018 - implicit return
  else:
    round(dollars * 100)


@implicit_return()
def area(shape: tuple[str, float]) -> str:
  """Describe the area of a ``('circle', r)`` or ``('square', side)`` shape."""
  match shape:
    case ('circle', radius):
      f'circle: {3.14159 * radius * radius:.1f}'
    case ('square', side):
      f'square: {side * side:.1f}'
    case _:
      'unknown shape'


def with_tax(price: float) -> float:
  """Add 25% tax to ``price``; an undecorated helper keeps its ordinary ``return``."""
  return price * 1.25


@implicit_return()
def total(prices: list[float]) -> float:
  """Sum ``prices`` with tax; ``return`` is refused anywhere in this body, so no nested def."""
  sum(with_tax(price) for price in prices)


if __name__ == '__main__':
  assert [grade(95), grade(80), grade(10)] == ['A', 'B', 'C']
  assert to_cents('12.34') == 1234
  assert to_cents('twelve') == 0
  assert area(('circle', 1.0)) == 'circle: 3.1'
  assert area(('square', 2.0)) == 'square: 4.0'
  assert area(('hexagon', 1.0)) == 'unknown shape'
  assert total([4.0, 8.0]) == 15.0

  print(f'grades: {grade(95)}, {grade(80)}, {grade(10)}')
  print(f'to_cents("12.34") = {to_cents("12.34")}, total([4, 8]) = {total([4.0, 8.0])}')
  print(f'{area(("circle", 1.0))} | {area(("square", 2.0))}')
