"""The three ImplicitReturnError subclasses, all raised when the decorator is applied.

Run: poetry run python examples/free_range/11_decoration_errors.py
See: docs/api-reference.md#error-classes
"""

from typing import Any, Callable

from modgud import (
  ExplicitReturnDisallowedError,
  ImplicitReturnError,
  MissingImplicitReturnError,
  UnsupportedConstructError,
  implicit_return,
)

# Left undecorated on purpose: each is decorated inside a try below, so the module still imports.


def explicit(x: int) -> int:
  """Use ``return``, which implicit-return mode forbids."""
  return x


def no_else(x: int) -> int:
  """End in an ``if`` with no ``else``, so one path has no value."""
  if x > 0:
    x  # noqa: B018 - implicit return


def loop_tail(items: list[int]) -> int:
  """End in a ``for`` loop, which has no value to return."""
  for item in items:
    print(item)


def decoration_error(func: Callable[..., Any]) -> ImplicitReturnError | None:
  """Apply ``@implicit_return()`` to ``func`` and return the error it raises, if any."""
  caught: ImplicitReturnError | None = None
  try:
    implicit_return()(func)
  except ImplicitReturnError as error:
    caught = error
  return caught


if __name__ == '__main__':
  expected: dict[Callable[..., Any], type[ImplicitReturnError]] = {
    explicit: ExplicitReturnDisallowedError,
    no_else: MissingImplicitReturnError,
    loop_tail: UnsupportedConstructError,
  }
  for func, error_type in expected.items():
    caught: ImplicitReturnError | None = decoration_error(func)
    assert caught is not None and type(caught) is error_type, f'{func.__name__}: {caught!r}'
    assert isinstance(caught, SyntaxError)  # the whole family subclasses SyntaxError
    print(f'{func.__name__}: {error_type.__name__}: {caught.msg}')
