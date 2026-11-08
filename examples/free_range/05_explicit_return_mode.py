"""Guards without the AST rewrite: implicit_return=False and one trailing ``return``.

Run: poetry run python examples/free_range/05_explicit_return_mode.py
See: docs/api-reference.md#guarded_expression
"""

from modgud import GuardClauseError, Guards, guarded_expression


@guarded_expression(Guards.not_empty('readings'), implicit_return=False)
def average(readings: list[float]) -> float:
  """Return the mean of ``readings``; the guard has already ruled out an empty list.

  :param readings: Sensor readings.
  :returns: Their arithmetic mean.
  :raises GuardClauseError: If ``readings`` is empty.
  """
  return sum(readings) / len(readings)


@guarded_expression(Guards.positive('x'), implicit_return=False)
def forgetful(x: int) -> None:
  """Compute ``x * 2`` and drop it: explicit mode means what it says."""
  x * 2


if __name__ == '__main__':
  assert average([1.0, 2.0, 6.0]) == 3.0

  refusal: GuardClauseError | None = None
  try:
    average([])
  except GuardClauseError as error:
    refusal = error
  assert str(refusal) == 'readings cannot be empty'

  # No rewrite happened, so the bare tail expression is not returned.
  assert forgetful(21) is None

  print(f'average([1, 2, 6]) = {average([1.0, 2.0, 6.0])}')
  print(f'average([]) refused: {refusal}; forgetful(21) = {forgetful(21)}')
