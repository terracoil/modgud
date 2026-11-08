"""The README quick start, verbatim in shape: a guarded static method with an implicit return.

Run: poetry run python examples/classy/01_quick_start.py
See: docs/api-reference.md#guarded_expression
"""

from modgud import GuardClauseError, Guards, guarded_expression


class DiscountCalculator:
  """Discounts for prices between 1 and 100."""

  @staticmethod
  @guarded_expression(
    Guards.positive('x'),
    Guards.in_range(1, 100, 'x'),
  )
  def calculate(x: float) -> float:
    """Return the discount on ``x``: 20% from 50 up, 10% below.

    :param x: Price; the guards refuse anything outside 1-100.
    :returns: The discount amount (the last expression of whichever branch ran).
    :raises GuardClauseError: If ``x`` is not positive or not in range.
    """
    if x >= 50:
      x * 0.2
    else:
      x * 0.1

  @classmethod
  def demo(cls) -> None:
    """Check the README's three claims, then show them."""
    assert cls.calculate(75) == 15.0
    assert cls.calculate(25) == 2.5

    refusal: GuardClauseError | None = None
    try:
      cls.calculate(-10)
    except GuardClauseError as error:
      refusal = error
    assert str(refusal) == 'x must be positive'

    print(f'calculate(75) = {cls.calculate(75)}, calculate(25) = {cls.calculate(25)}')
    print(f'calculate(-10) refused: {refusal}')


if __name__ == '__main__':
  DiscountCalculator.demo()
