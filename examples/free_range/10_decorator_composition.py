"""Stacking order: modgud's two decorators, other decorators, and the metadata that survives.

Run: poetry run python examples/free_range/10_decorator_composition.py
See: docs/api-reference.md#decorator-order
"""

import functools
import inspect
from typing import Any, Callable

from modgud import GuardClauseError, Guards, guarded_expression, implicit_return

CALLS: list[str] = []


def counted(func: Callable[..., Any]) -> Callable[..., Any]:
  """Record each call by name; stands in for any third-party decorator."""

  @functools.wraps(func)
  def wrapper(*args: Any, **kwargs: Any) -> Any:
    CALLS.append(func.__name__)
    return func(*args, **kwargs)

  return wrapper


@guarded_expression(Guards.positive('x'), implicit_return=False)  # right: guards outside
@implicit_return()
def right(x: int) -> int:
  """Double ``x``, guarded."""
  x * 2


@counted  # right: other decorators go outside modgud
@guarded_expression(Guards.positive('x'))
def counted_outside(x: int) -> int:
  """Triple ``x``, and the call is counted."""
  x * 3


@guarded_expression(Guards.positive('x'))  # wrong: modgud rebuilds from source, so
@counted  # anything between it and the ``def`` is discarded
def counted_inside(x: int) -> int:
  """Triple ``x``; the counter never sees the call."""
  x * 3


if __name__ == '__main__':
  refusal: GuardClauseError | None = None
  try:
    right(-1)
  except GuardClauseError as error:
    refusal = error
  assert str(refusal) == 'x must be positive'

  stacking: TypeError | None = None
  try:

    @implicit_return()  # wrong: the rewrite would re-read the source and drop the guard below
    @guarded_expression(Guards.positive('x'), implicit_return=False)
    def wrong(x: int) -> int:
      """Double ``x``; never decorated, the stack is refused."""
      x * 2

  except TypeError as error:
    stacking = error
  assert str(stacking).startswith('@implicit_return() must sit below @guarded_expression')

  assert counted_outside(2) == counted_inside(2) == 6
  assert CALLS == ['counted_outside']

  assert right.__name__ == 'right' and right.__doc__ == 'Double ``x``, guarded.'
  assert list(inspect.signature(right).parameters) == ['x']
  assert right.__annotations__ == {'x': int, 'return': int}

  print(f'right(-1) refused: {refusal}; counted: {CALLS}')
  print(f'wrong order refused at decoration: {stacking}')
  print(f'metadata kept: {right.__name__}{inspect.signature(right)}')
