"""The four failure strategies: raise, return the error, return a value, call a handler.

Run: poetry run python examples/free_range/03_failure_strategies.py
See: docs/api-reference.md#guardfailureenum
"""

from typing import Any

from modgud import (
  CommonGuards,
  GuardClauseError,
  GuardFailureEnum,
  GuardFunction,
  guarded_expression,
)

AMOUNT: GuardFunction = CommonGuards.positive('amount')


class PaymentError(Exception):
  """Raised instead of GuardClauseError when a payment amount is refused."""


def explain(errors: list[str], *args: Any, **kwargs: Any) -> dict[str, Any]:
  """Turn guard failures into an error payload; handlers see the call's arguments too."""
  return {'status': 400, 'errors': errors, 'args': args}


@guarded_expression(AMOUNT, on_failure=PaymentError)  # ERROR_RAISE is the default strategy
def charge(amount: float) -> str:
  """Charge ``amount``, raising PaymentError when it isn't positive."""
  f'charged {amount:.2f}'


@guarded_expression(AMOUNT, strategy=GuardFailureEnum.ERROR_RETURN)
def charge_or_error(amount: float) -> str | GuardClauseError:
  """Charge ``amount``, or hand back the GuardClauseError instead of raising it."""
  f'charged {amount:.2f}'


@guarded_expression(AMOUNT, strategy=GuardFailureEnum.RETURN_VALUE, on_failure='declined')
def charge_or_decline(amount: float) -> str:
  """Charge ``amount``, or return ``'declined'`` as-is."""
  f'charged {amount:.2f}'


@guarded_expression(AMOUNT, strategy=GuardFailureEnum.CALL_HANDLER, on_failure=explain)
def charge_or_explain(amount: float) -> str | dict[str, Any]:
  """Charge ``amount``, or return whatever ``explain`` makes of the failure."""
  f'charged {amount:.2f}'


if __name__ == '__main__':
  assert charge(5) == charge_or_error(5) == charge_or_decline(5) == 'charged 5.00'

  raised: PaymentError | None = None
  try:
    charge(-1)
  except PaymentError as error:
    raised = error
  assert str(raised) == 'amount must be positive'

  returned: Any = charge_or_error(-1)
  assert isinstance(returned, GuardClauseError) and str(returned) == 'amount must be positive'

  assert charge_or_decline(-1) == 'declined'
  assert charge_or_explain(-1) == {
    'status': 400,
    'errors': ['amount must be positive'],
    'args': (-1,),
  }

  print(f'raise -> {raised!r}')
  print(f'return error -> {returned!r}')
  print(f'return value -> {charge_or_decline(-1)!r}')
  print(f'call handler -> {charge_or_explain(-1)!r}')
