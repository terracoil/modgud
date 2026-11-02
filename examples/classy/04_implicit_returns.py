"""Standalone @implicit_return() on instance, static and class methods.

Run: poetry run python examples/classy/04_implicit_returns.py
See: docs/api-reference.md#implicit_return
"""

from modgud import implicit_return


class Gradebook:
  """Grades, money parsing and shapes, every result an implicit return."""

  def __init__(self, top: int = 90, good: int = 75) -> None:
    """Set the score needed for an A and for a B."""
    self.top: int = top
    self.good: int = good

  @implicit_return()
  def grade(self, score: int) -> str:
    """Map ``score`` to a letter using this gradebook's thresholds."""
    if score >= self.top:
      'A'
    elif score >= self.good:
      'B'
    else:
      'C'

  @staticmethod
  @implicit_return()
  def to_cents(text: str) -> int:
    """Parse ``text`` as dollars and return cents, or 0 if it isn't a number."""
    try:
      dollars: float = float(text)
      dollars  # noqa: B018 - the try body needs a tail; else replaces it on success
    except ValueError:
      0  # noqa: B018 - implicit return
    else:
      round(dollars * 100)

  @classmethod
  @implicit_return()
  def area(cls, shape: tuple[str, float]) -> str:
    """Describe the area of a ``('circle', r)`` or ``('square', side)`` shape."""
    match shape:
      case ('circle', radius):
        f'{cls.__name__}: circle {3.14159 * radius * radius:.1f}'
      case ('square', side):
        f'{cls.__name__}: square {side * side:.1f}'
      case _:
        'unknown shape'

  @staticmethod
  def with_tax(price: float) -> float:
    """Add 25% tax to ``price``; an undecorated helper keeps its ordinary ``return``."""
    return price * 1.25

  @implicit_return()
  def total(self, prices: list[float]) -> float:
    """Sum ``prices`` with tax; ``return`` is refused anywhere in this body, so no nested def."""
    sum(self.with_tax(price) for price in prices)

  @classmethod
  def demo(cls) -> None:
    """Exercise every branch once."""
    book: Gradebook = cls()
    assert [book.grade(95), book.grade(80), book.grade(10)] == ['A', 'B', 'C']
    assert cls(top=99).grade(95) == 'B'
    assert cls.to_cents('12.34') == 1234 and cls.to_cents('twelve') == 0
    assert cls.area(('circle', 1.0)) == 'Gradebook: circle 3.1'
    assert cls.area(('hexagon', 1.0)) == 'unknown shape'
    assert book.total([4.0, 8.0]) == 15.0

    print(f'grades: {book.grade(95)}, {book.grade(80)}, {book.grade(10)}')
    print(f'{cls.area(("square", 2.0))}; total([4, 8]) = {book.total([4.0, 8.0])}')


if __name__ == '__main__':
  Gradebook.demo()
