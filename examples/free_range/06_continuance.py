"""Collect several guard failures at once with ``continuance``, then unpack the ExceptionGroup.

Run: poetry run python examples/free_range/06_continuance.py
See: docs/api-reference.md#collecting-multiple-failures
"""

from modgud import (
  CommonGuards,
  GuardClauseError,
  GuardFailureEnum,
  GuardFunction,
  guarded_expression,
)

CHECKS: tuple[GuardFunction, ...] = (
  CommonGuards.positive('qty'),
  CommonGuards.in_range(1, 10, 'qty'),
  CommonGuards.not_empty('sku', position=1),
  CommonGuards.matches_pattern(r'^[A-Z]{3}-\d+$', 'sku', position=1),
)


def short_sku(qty: int, sku: str) -> bool | str:
  """Refuse SKUs over eight characters; raises TypeError when ``sku`` is None."""
  return len(sku) <= 8 or 'sku must be at most 8 characters'


@guarded_expression(*CHECKS)  # continuance=0: stop at the first failure
def first_only(qty: int, sku: str) -> str:
  """Reserve ``qty`` units of ``sku``, reporting one problem at a time."""
  f'{qty} x {sku}'


@guarded_expression(*CHECKS, continuance=3)  # up to 1 + 3 failures
def every_problem(qty: int, sku: str) -> str:
  """Reserve ``qty`` units of ``sku``, reporting up to four problems at once."""
  f'{qty} x {sku}'


@guarded_expression(*CHECKS, continuance=3, strategy=GuardFailureEnum.ERROR_RETURN)
def problems_returned(qty: int, sku: str) -> str | BaseException:
  """Return the ExceptionGroup instead of raising it; otherwise like ``every_problem``."""
  f'{qty} x {sku}'


@guarded_expression(CommonGuards.not_none('sku', position=1), short_sku, continuance=5)
def cascade_safe(qty: int, sku: str) -> str:
  """Stop quietly when ``short_sku`` raises after not_none failed: one error, no group."""
  f'{qty} x {sku}'


if __name__ == '__main__':
  assert first_only(2, 'ABC-1') == every_problem(2, 'ABC-1') == '2 x ABC-1'

  first: GuardClauseError | None = None
  try:
    first_only(-1, '')
  except GuardClauseError as error:
    first = error
  assert str(first) == 'qty must be positive'

  collected: list[str] = []
  try:
    every_problem(-1, '')
  except* GuardClauseError as group:
    collected = [str(error) for error in group.exceptions]
  assert len(collected) == 4 and collected[0] == 'qty must be positive'

  returned: BaseException | str = problems_returned(-1, 'abc')
  assert isinstance(returned, ExceptionGroup) and len(returned.exceptions) == 3  # 'abc' isn't empty

  cascaded: GuardClauseError | None = None
  try:
    cascade_safe(1, None)
  except GuardClauseError as error:
    cascaded = error
  assert str(cascaded) == 'sku cannot be None'

  print(f'first only: {first}; cascade-safe: {cascaded}')
  print('every problem:', *collected, sep='\n  ')
