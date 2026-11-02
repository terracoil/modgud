"""Decorated functions and their undecorated twins for the signature regression suite.

Each ``*_twin`` has exactly the signature and docstring of the decorated function above it, so
``tests/test_signatures.py`` can compare what ``inspect`` reports for the two. They live in a
real module because the implicit-return rewrite reads the source from disk.

No ``from __future__ import annotations`` here on purpose: both halves of every pair must
evaluate their annotations the same way, and the decorated half is what is under test.
"""

from typing import Any

from modgud import CommonGuards, guarded_expression, implicit_return

DEFAULT_LIMIT: int = 10
SENTINEL: object = object()  # compared by identity, so a re-evaluated default would show up
FIRST_NOT_NONE = CommonGuards.not_none('a')


def accept_all(*args: Any, **kwargs: Any) -> bool:
  """Guard that always passes, for signatures with no positional parameter to inspect."""
  return True


# Positional-only, two of them defaulted, then a positional-or-keyword default.
@guarded_expression(FIRST_NOT_NONE)
def posonly(a: int, b: int = 2, /, c: int = 3) -> int:
  """Add three numbers, the first two positional-only."""
  a + b + c


def posonly_twin(a: int, b: int = 2, /, c: int = 3) -> int:
  """Add three numbers, the first two positional-only."""
  return a + b + c


# Keyword-only with a default followed by a keyword-only without one.
@guarded_expression(FIRST_NOT_NONE, implicit_return=False)
def kwonly(a: int, *, k: int = 3, m: str) -> str:
  """Repeat m (a + k) times."""
  return m * (a + k)


def kwonly_twin(a: int, *, k: int = 3, m: str) -> str:
  """Repeat m (a + k) times."""
  return m * (a + k)


# Annotated *args / **kwargs.
@guarded_expression(accept_all)
def star_args(*args: int, **kwargs: str) -> tuple[int, int]:
  """Sum the positionals and count the keywords."""
  (sum(args), len(kwargs))


def star_args_twin(*args: int, **kwargs: str) -> tuple[int, int]:
  """Sum the positionals and count the keywords."""
  return (sum(args), len(kwargs))


# Defaults naming module globals; the rewrite must reuse them, not re-evaluate them.
@implicit_return()
def module_default(a: int, limit: int = DEFAULT_LIMIT, marker: object = SENTINEL) -> bool:
  """Report whether a is within limit and the marker is the module sentinel."""
  a <= limit and marker is SENTINEL  # noqa: B018


def module_default_twin(a: int, limit: int = DEFAULT_LIMIT, marker: object = SENTINEL) -> bool:
  """Report whether a is within limit and the marker is the module sentinel."""
  return a <= limit and marker is SENTINEL


# Two guarded layers: only the inner one rewrites, the outer one wraps a wrapper.
@guarded_expression(FIRST_NOT_NONE)
@guarded_expression(CommonGuards.positive('a'))
def stacked(a: int, /, *, scale: float = 1.5) -> float:
  """Scale a, which must be positive."""
  a * scale


def stacked_twin(a: int, /, *, scale: float = 1.5) -> float:
  """Scale a, which must be positive."""
  return a * scale


# Guards with an explicit-return wrapper over a standalone implicit-return rewrite.
@guarded_expression(FIRST_NOT_NONE, implicit_return=False)
@implicit_return()
def layered(a: 'int', note: str = 'n/a') -> 'str':
  """Join a and note; the annotations are strings and must stay strings."""
  f'{a}:{note}'


def layered_twin(a: 'int', note: str = 'n/a') -> 'str':
  """Join a and note; the annotations are strings and must stay strings."""
  return f'{a}:{note}'


@guarded_expression(FIRST_NOT_NONE)
async def fetch(a: int, /, *, retries: int = 3) -> str:
  """Describe a fetch of a with some retries."""
  f'{a}x{retries}'


async def fetch_twin(a: int, /, *, retries: int = 3) -> str:
  """Describe a fetch of a with some retries."""
  return f'{a}x{retries}'


@implicit_return()
async def fetch_plain(a: int, retries: int = DEFAULT_LIMIT) -> int:
  """Multiply a by the retry count."""
  a * retries


async def fetch_plain_twin(a: int, retries: int = DEFAULT_LIMIT) -> int:
  """Multiply a by the retry count."""
  return a * retries


class Pricing:
  """Defaults that name class attributes, which only exist while the class body runs."""

  rate: int = 5
  cap: int = 100

  @guarded_expression(CommonGuards.positive('qty'))
  def total(self, qty: int, rate: int = rate, *, cap: int = cap) -> int:
    """Price qty items at rate, never more than cap."""
    min(qty * rate, cap)

  def total_twin(self, qty: int, rate: int = rate, *, cap: int = cap) -> int:
    """Price qty items at rate, never more than cap."""
    return min(qty * rate, cap)

  @classmethod
  @implicit_return()
  def scaled(cls, qty: int, /, factor: int = rate) -> int:
    """Scale qty by factor, which defaults to the class rate."""
    qty * factor

  @classmethod
  def scaled_twin(cls, qty: int, /, factor: int = rate) -> int:
    """Scale qty by factor, which defaults to the class rate."""
    return qty * factor
