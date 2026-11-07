"""``eop_match``: Elixir's ``match?`` as a boolean expression.

``eop_match(pattern, value)`` tells whether ``value`` matches ``pattern``. A guard goes inside
the pattern with ``eop_when``, and captures are usable only in that guard. It needs no
temporary, so it fits anywhere, including a comprehension filter.

Run: poetry run python examples/free_range/15_eop_match.py
See: docs/api-reference.md#eop_match
"""

from dataclasses import dataclass

from modgud import eop_match, eop_var, eop_when, implicit_return


@dataclass(frozen=True)
class Point:
  """A point on a plane."""

  x: int
  y: int


@implicit_return()
def on_y_axis(shape: object) -> bool:
  """Tell whether ``shape`` is a point on the y axis."""
  eop_match(Point(0, eop_var._), shape)


@implicit_return()
def above_origin(shapes: list[object]) -> list[object]:
  """Keep the points straight above the origin; the guard reads the capture."""
  [s for s in shapes if eop_match(eop_when(Point(0, eop_var.y), eop_var.y > 0), s)]


@implicit_return()
def looks_like_a_record(value: object) -> bool:
  """Match any mapping with an ``id`` key."""
  eop_match({'id': eop_var._}, value)


if __name__ == '__main__':
  assert on_y_axis(Point(0, 9)) and not on_y_axis(Point(1, 9)) and not on_y_axis('nope')
  assert above_origin([Point(0, 1), Point(0, -1), Point(2, 2)]) == [Point(0, 1)]
  assert looks_like_a_record({'id': 1, 'name': 'x'}) and not looks_like_a_record({'name': 'x'})

  print(f'on_y_axis(Point(0, 9)) = {on_y_axis(Point(0, 9))}')
  print(f'above_origin -> {above_origin([Point(0, 1), Point(0, -1), Point(2, 2)])}')
