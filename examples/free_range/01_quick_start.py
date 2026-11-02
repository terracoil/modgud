"""One guard, one implicit return, one refusal: the smallest useful modgud function.

Run: poetry run python examples/free_range/01_quick_start.py
See: docs/api-reference.md#guarded_expression
"""

from modgud import CommonGuards, GuardClauseError, guarded_expression


@guarded_expression(CommonGuards.positive('price'))
def discount(price: float) -> float:
  """Return the discount on ``price``: 20% from 50 up, 10% below.

  :param price: Item price; the guard refuses anything that isn't positive.
  :returns: The discount amount (the last expression of whichever branch ran).
  :raises GuardClauseError: If ``price`` is zero or negative.
  """
  if price >= 50:
    price * 0.2
  else:
    price * 0.1


if __name__ == '__main__':
  assert discount(75) == 15.0
  assert discount(25) == 2.5
  assert discount(price=25) == 2.5  # keyword calls are checked too

  refusal: GuardClauseError | None = None
  try:
    discount(-10)
  except GuardClauseError as error:
    refusal = error
  assert str(refusal) == 'price must be positive'

  print(f'discount(75) = {discount(75)}, discount(25) = {discount(25)}')
  print(f'discount(-10) refused: {refusal}')
