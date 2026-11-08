"""The four failure strategies on instance methods; the handler also receives ``self``.

Run: poetry run python examples/classy/03_failure_strategies.py
See: docs/api-reference.md#guardfailureenum
"""

from typing import Any

from modgud import GuardClauseError, GuardFailureEnum, Guards, guarded_expression


class Checkout:
  """One checkout, four ways to say no."""

  def __init__(self, currency: str = 'EUR') -> None:
    """Remember the currency every charge is quoted in."""
    self.currency: str = currency

  @staticmethod
  def explain(errors: list[str], *args: Any, **kwargs: Any) -> dict[str, Any]:
    """Shape failures as a 400 payload; on a method, ``args[0]`` is the receiver."""
    return {'status': 400, 'errors': errors, 'args': args}

  @guarded_expression(Guards.positive('amount'))  # ERROR_RAISE + GuardClauseError
  def charge(self, amount: float) -> str:
    """Charge ``amount`` or raise."""
    f'charged {amount:.2f} {self.currency}'

  @guarded_expression(Guards.positive('amount'), strategy=GuardFailureEnum.ERROR_RETURN)
  def charge_or_error(self, amount: float) -> str | GuardClauseError:
    """Charge ``amount`` or hand back the GuardClauseError."""
    f'charged {amount:.2f} {self.currency}'

  @guarded_expression(
    Guards.positive('amount'),
    strategy=GuardFailureEnum.RETURN_VALUE,
    on_failure='declined',
  )
  def charge_or_decline(self, amount: float) -> str:
    """Charge ``amount`` or return ``'declined'``."""
    f'charged {amount:.2f} {self.currency}'

  @guarded_expression(
    Guards.positive('amount'),
    strategy=GuardFailureEnum.CALL_HANDLER,
    on_failure=explain,
  )
  def charge_or_explain(self, amount: float) -> str | dict[str, Any]:
    """Charge ``amount`` or return what ``explain`` makes of the failure."""
    f'charged {amount:.2f} {self.currency}'

  @classmethod
  def demo(cls) -> None:
    """Refuse the same bad amount four ways."""
    till: Checkout = cls()
    assert till.charge(5) == till.charge_or_decline(5) == 'charged 5.00 EUR'

    raised: GuardClauseError | None = None
    try:
      till.charge(-1)
    except GuardClauseError as error:
      raised = error
    assert str(raised) == 'amount must be positive'

    returned: Any = till.charge_or_error(-1)
    assert isinstance(returned, GuardClauseError) and str(returned) == str(raised)
    assert till.charge_or_decline(-1) == 'declined'
    explained: dict[str, Any] = till.charge_or_explain(-1)
    assert explained['errors'] == ['amount must be positive']
    assert explained['args'] == (till, -1)  # guards skip the receiver; handlers don't

    print(f'raise: {raised!r} | return: {returned!r} | value: {till.charge_or_decline(-1)!r}')
    print(f'handler: {explained["errors"]}, receiver passed: {explained["args"][0] is till}')


if __name__ == '__main__':
  Checkout.demo()
