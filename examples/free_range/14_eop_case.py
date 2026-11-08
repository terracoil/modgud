"""``eop_case``: Elixir's ``case`` as an expression, with real structural patterns.

A pattern is written as an expression: ``Point(0, eop_var.y)`` captures ``y``, ``eop_var._``
matches anything, and ``eop_when(pattern, guard)`` adds a guard. Captures are visible only in
their own clause. The subject is evaluated once, and ``default=`` is required.

Run: poetry run python examples/free_range/14_eop_case.py
See: docs/api-reference.md#eop_case
"""

from dataclasses import dataclass

from modgud import eop_case, eop_clause, eop_var, eop_when, implicit_return


@dataclass(frozen=True)
class Point:
  """A point on a plane."""

  x: int
  y: int


@implicit_return()
def describe(shape: object) -> str:
  """Describe where ``shape`` sits; the tail expression is the return value."""
  eop_case(
    shape,
    eop_clause(eop_when(Point(0, eop_var.y), eop_var.y > 0), f'above the origin at {eop_var.y}'),
    eop_clause(Point(eop_var.x, 0), f'on the x axis at {eop_var.x}'),
    eop_clause(Point(eop_var._, eop_var._), 'somewhere else'),
    default='not a point',
  )


@implicit_return()
def head(values: object) -> str:
  """Sequence and mapping patterns, with a star and a rest capture."""
  eop_case(
    values,
    eop_clause([], 'empty'),
    eop_clause([eop_var.first, *eop_var.rest], f'{eop_var.first} and {len(eop_var.rest)} more'),
    eop_clause({'id': eop_var.i, **eop_var.rest}, f'#{eop_var.i} with {sorted(eop_var.rest)}'),
    default='neither',
  )


@implicit_return()
def labels(shapes: list[object]) -> list[str]:
  """Use ``eop_case`` inside a comprehension, where a ``match`` statement cannot go."""
  [
    eop_case(s, eop_clause(Point(eop_var.x, eop_var._), f'x={eop_var.x}'), default='?')
    for s in shapes
  ]


if __name__ == '__main__':
  assert describe(Point(0, 2)) == 'above the origin at 2'
  assert describe(Point(0, -2)) == 'somewhere else'  # the guard failed, so the next clause ran
  assert describe(Point(3, 0)) == 'on the x axis at 3'
  assert describe('circle') == 'not a point'
  assert head([]) == 'empty' and head([1, 2, 3]) == '1 and 2 more'
  assert head({'id': 7, 'k': 1}) == "#7 with ['k']" and head(42) == 'neither'
  assert labels([Point(1, 1), 'x']) == ['x=1', '?']

  print(f'describe: {describe(Point(0, 2))}; {describe(Point(3, 0))}')
  print(f'head: {head([1, 2, 3])}; labels: {labels([Point(1, 1), "x"])}')
