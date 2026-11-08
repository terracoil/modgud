"""A tour of all nine CommonGuards, and how they find the argument they check.

Run: poetry run python examples/free_range/02_common_guards.py
See: docs/api-reference.md#commonguards
"""

from enum import Enum
from pathlib import Path
from typing import Any, Callable

from modgud import CommonGuards, GuardClauseError, guarded_expression


class Color(Enum):
  """Colours the shop can actually paint."""

  RED = 'red'
  GREEN = 'green'


def refusal(call: Callable[[], Any]) -> str:
  """Return the guard message raised by ``call``, or ``'accepted'``."""
  message: str = 'accepted'
  try:
    call()
  except GuardClauseError as error:
    message = str(error)
  return message


@guarded_expression(
  CommonGuards.not_none('name'),
  CommonGuards.not_empty('name'),
  CommonGuards.type_check(str, 'name'),
  CommonGuards.matches_pattern(r'^[a-z_]+$', 'name'),
)
def slug(name: str) -> str:
  """Turn a snake_case ``name`` into a kebab-case slug."""
  name.replace('_', '-')


# Lookup is by keyword first, then by position (default 0). The second
# parameter needs position=1, or a positional call would check ``qty`` twice.
@guarded_expression(
  CommonGuards.positive('qty'),
  CommonGuards.in_range(1, 10, 'qty'),
  CommonGuards.valid_enum(Color, 'color', position=1),
)
def order(qty: int, color: str) -> str:
  """Describe an order of ``qty`` items painted ``color``."""
  f'{qty} x {Color(color).name}'


@guarded_expression(
  CommonGuards.valid_url('url'),
  CommonGuards.valid_file_path('path', position=1, must_be_file=True),
)
def publish(url: str, path: str) -> str:
  """Pretend to upload the file at ``path`` to ``url``."""
  f'{Path(path).name} -> {url}'


if __name__ == '__main__':
  assert slug('free_range') == 'free-range'
  assert refusal(lambda: slug(None)) == 'name cannot be None'
  assert refusal(lambda: slug('')) == 'name cannot be empty'
  assert refusal(lambda: slug(42)) == 'name must be of type str'
  assert refusal(lambda: slug('Free Range')) == 'name must match pattern ^[a-z_]+$'

  assert order(3, 'red') == order(qty=3, color='red') == '3 x RED'
  assert refusal(lambda: order(0, 'red')) == 'qty must be positive'
  assert refusal(lambda: order(11, 'red')) == 'qty must be between 1 and 10'
  assert refusal(lambda: order(3, 'mauve')) == "color must be one of ['red', 'green']: got mauve"

  assert publish('https://example.com', __file__).endswith('-> https://example.com')
  assert refusal(lambda: publish('example.com', __file__)).startswith(
    'url must use one of http/https'
  )
  assert refusal(lambda: publish('https://x.io', '/nowhere')) == 'path does not exist: /nowhere'

  print(f'{slug("free_range")!r}, {order(3, "red")!r}; all nine guards checked')
