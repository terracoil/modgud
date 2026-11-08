"""Collect several guard failures from a method with ``continuance``; unpack them with except*.

Run: poetry run python examples/classy/06_continuance.py
See: docs/api-reference.md#collecting-multiple-failures
"""

from typing import ClassVar

from modgud import (
  CommonGuards,
  GuardClauseError,
  GuardFailureEnum,
  GuardFunction,
  guarded_expression,
)


class Warehouse:
  """Reserve stock, reporting every problem with an order at once."""

  CHECKS: ClassVar[tuple[GuardFunction, ...]] = (
    CommonGuards.positive('qty'),
    CommonGuards.in_range(1, 10, 'qty'),
    CommonGuards.not_empty('sku', position=1),
    CommonGuards.matches_pattern(r'^[A-Z]{3}-\d+$', 'sku', position=1),
  )

  @staticmethod
  def short_sku(qty: int, sku: str) -> bool | str:
    """Refuse SKUs over eight characters; raises TypeError when ``sku`` is None."""
    return len(sku) <= 8 or 'sku must be at most 8 characters'

  @guarded_expression(*CHECKS, continuance=3)  # up to 1 + 3 failures
  def reserve(self, qty: int, sku: str) -> str:
    """Reserve ``qty`` units of ``sku``."""
    f'{qty} x {sku}'

  @guarded_expression(*CHECKS, continuance=3, strategy=GuardFailureEnum.ERROR_RETURN)
  def try_reserve(self, qty: int, sku: str) -> str | BaseException:
    """Reserve, or return the ExceptionGroup instead of raising it."""
    f'{qty} x {sku}'

  @guarded_expression(CommonGuards.not_none('sku', position=1), short_sku, continuance=5)
  def reserve_safely(self, qty: int, sku: str) -> str:
    """Stop quietly when ``short_sku`` raises after not_none failed: one error, no group."""
    f'{qty} x {sku}'

  @classmethod
  def demo(cls) -> None:
    """Show a full report, a returned group, and cascade safety."""
    depot: Warehouse = cls()
    assert depot.reserve(2, 'ABC-1') == '2 x ABC-1'

    collected: list[str] = []
    try:
      depot.reserve(-1, '')
    except* GuardClauseError as group:
      collected = [str(error) for error in group.exceptions]
    assert len(collected) == 4 and collected[-1].startswith('sku must match pattern')

    returned: BaseException | str = depot.try_reserve(-1, 'abc')
    assert isinstance(returned, ExceptionGroup) and len(returned.exceptions) == 3

    cascaded: GuardClauseError | None = None
    try:
      depot.reserve_safely(1, None)
    except GuardClauseError as error:
      cascaded = error
    assert str(cascaded) == 'sku cannot be None'

    print('every problem:', *collected, sep='\n  ')
    print(f'returned: {returned!r}; cascade-safe: {cascaded}')


if __name__ == '__main__':
  Warehouse.demo()
