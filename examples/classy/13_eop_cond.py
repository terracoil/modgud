"""``eop_cond`` on methods: Elixir's ``cond`` as an expression inside a class.

Run: poetry run python examples/classy/13_eop_cond.py
See: docs/api-reference.md#eop_cond
"""

from modgud import eop_clause, eop_cond, implicit_return


class Thermostat:
  """Turns temperatures into words, one expression at a time."""

  def __init__(self, low: int = 15, high: int = 25) -> None:
    """Set the comfortable range."""
    self.low: int = low
    self.high: int = high

  @implicit_return()
  def verdict(self, degrees: int) -> str:
    """Say whether ``degrees`` is cold, hot or fine; clauses are tested in order."""
    eop_cond(
      eop_clause(degrees < self.low, 'cold'),
      eop_clause(degrees > self.high, 'hot'),
      default='fine',
    )

  @staticmethod
  @implicit_return()
  def truth(value: object) -> str:
    """Apply Elixir's rule: only ``None`` and ``False`` are false."""
    eop_cond(eop_clause(value, 'true'), default='false')

  @classmethod
  @implicit_return()
  def verdicts(cls, readings: list[int]) -> list[str]:
    """Use ``eop_cond`` inside a comprehension."""
    [eop_cond(eop_clause(r > 30, 'alarm'), default=cls().verdict(r)) for r in readings]

  @classmethod
  def demo(cls) -> None:
    """Exercise every clause once."""
    unit: Thermostat = cls()
    assert [unit.verdict(5), unit.verdict(35), unit.verdict(20)] == ['cold', 'hot', 'fine']
    samples: list[object] = [[], 0, None, False]
    assert [cls.truth(v) for v in samples] == ['true', 'true', 'false', 'false']
    assert cls.verdicts([5, 40]) == ['cold', 'alarm']

    print(f'verdicts: {unit.verdict(5)}, {unit.verdict(35)}, {unit.verdict(20)}')
    print(f'truth([]) = {cls.truth([])}')


if __name__ == '__main__':
  Thermostat.demo()
