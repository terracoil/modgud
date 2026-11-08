"""Module-level fixtures for the ``eop_`` form tests; the rewrite needs source on disk."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Any

from modgud import (
  CommonGuards,
  eop_case,
  eop_clause,
  eop_cond,
  eop_match,
  eop_var,
  eop_when,
  guarded_expression,
  implicit_return,
)


@dataclass(frozen=True)
class Point:
  """A point on a plane."""

  x: int
  y: int


@dataclass(frozen=True)
class Circle:
  """A circle with a radius."""

  r: int


class Color(Enum):
  """Three colours, for value patterns."""

  RED = 1
  GREEN = 2
  BLUE = 3


LIMIT: int = 5
CALLS: list[str] = []


def note(label: str, value: Any = True) -> Any:
  """Record that an expression ran, then hand back ``value``."""
  CALLS.append(label)
  return value


# ---------------------------------------------------------------- eop_cond


@implicit_return()
def sign(x: int) -> str:
  """Name the sign of ``x``."""
  eop_cond(eop_clause(x < 0, 'negative'), eop_clause(x == 0, 'zero'), default='positive')


@implicit_return()
def elixir_truth(value: object) -> str:
  """Tell whether ``value`` counts as true under Elixir's rule."""
  eop_cond(eop_clause(value, 'true'), default='false')


@implicit_return()
def lazy_cond(x: int) -> str:
  """Run only the selected test and value; the call log proves it."""
  eop_cond(
    eop_clause(note('t1', x > 10), note('v1', 'big')),
    eop_clause(note('t2', x > 0), note('v2', 'small')),
    default=note('d', 'none'),
  )


@implicit_return()
def nested_cond(x: int, y: int) -> str:
  """Nest an ``eop_cond`` inside another one's value."""
  eop_cond(
    eop_clause(x > 0, eop_cond(eop_clause(y > 0, 'both'), default='x only')),
    default='neither',
  )


@implicit_return()
def cond_in_comprehension(values: list[int]) -> list[str]:
  """``eop_cond`` as a comprehension element."""
  [eop_cond(eop_clause(v % 2 == 0, 'even'), default='odd') for v in values]


@implicit_return()
def cond_in_lambda(threshold: int) -> Any:
  """``eop_cond`` inside a lambda body."""
  lambda v: eop_cond(eop_clause(v > threshold, 'over'), default='under')


@implicit_return()
def cond_in_while(limit: int) -> int:
  """``eop_cond`` as a ``while`` test."""
  count = 0
  while eop_cond(eop_clause(count < limit, True), default=False):
    count += 1
  count  # noqa: B018 - implicit return


@implicit_return()
def cond_raising_test(x: int) -> str:
  """Let a raising test propagate, as in Elixir."""
  eop_cond(eop_clause(1 // x > 0, 'ok'), default='no')


@implicit_return()
def cond_keyword_clause(x: int) -> str:
  """``eop_clause`` with keyword arguments."""
  eop_cond(eop_clause(test=x > 0, value='pos'), default='non-pos')


@implicit_return()
async def async_cond(x: int) -> str:
  """``eop_cond`` in a coroutine function."""
  eop_cond(eop_clause(x > 0, 'pos'), default='non-pos')


@guarded_expression(CommonGuards.not_none('x'))
def guarded_cond(x: int) -> str:
  """``eop_cond`` under ``guarded_expression``."""
  eop_cond(eop_clause(x > 0, 'pos'), default='non-pos')


@guarded_expression(implicit_return=False)
def explicit_cond(x: int) -> str:
  """``eop_cond`` in explicit-return mode."""
  label = eop_cond(eop_clause(x > 0, 'pos'), default='non-pos')
  return f'{label}!'


@guarded_expression(implicit_return=False)
def explicit_plain(x: int) -> int:
  """No form at all in explicit-return mode; must stay the same object."""
  return x + 1


class Shapes:
  """Methods using the forms."""

  @implicit_return()
  def sign(self, x: int) -> str:
    """``eop_cond`` in an instance method."""
    eop_cond(eop_clause(x < 0, 'negative'), default='non-negative')

  @staticmethod
  @implicit_return()
  def is_origin(shape: object) -> bool:
    """``eop_match`` in a static method."""
    eop_match(Point(0, 0), shape)

  @classmethod
  @implicit_return()
  def describe(cls, shape: object) -> str:
    """``eop_case`` in a class method."""
    eop_case(
      shape, eop_clause(Point(eop_var.x, eop_var.y), f'{eop_var.x},{eop_var.y}'), default='?'
    )


# ---------------------------------------------------------------- eop_match


@implicit_return()
def is_on_y_axis(shape: object) -> bool:
  """Match a plain class pattern with a wildcard."""
  eop_match(Point(0, eop_var._), shape)


@implicit_return()
def is_above_origin(shape: object) -> bool:
  """Match a guarded pattern."""
  eop_match(eop_when(Point(0, eop_var.y), eop_var.y > 0), shape)


@implicit_return()
def guard_truthy_only(value: object) -> bool:
  """Show that a truthy guard that is not ``True`` does not pass."""
  eop_match(eop_when(eop_var.v, eop_var.v), value)


@implicit_return()
def guard_raises(value: object) -> bool:
  """Show that a guard that raises counts as no match."""
  eop_match(eop_when(eop_var.v, eop_var.v.missing > 1), value)


@implicit_return()
def filter_on_axis(shapes: list[object]) -> list[object]:
  """``eop_match`` as a comprehension filter."""
  [shape for shape in shapes if eop_match(Point(0, eop_var._), shape)]


@implicit_return()
def match_in_first_iterable(shapes: list[object]) -> list[bool]:
  """``eop_match`` needs no walrus, so it may sit in a comprehension's first iterable."""
  [flag for flag in [eop_match(Point(0, eop_var._), s) for s in shapes]]


@implicit_return()
def match_captures_do_not_leak(shape: object) -> str:
  """After the match, ``y`` is the function's own local, not the capture."""
  y = 'untouched'
  eop_match(Point(0, eop_var.y), shape)
  y  # noqa: B018 - implicit return


@implicit_return()
def match_bare_name(value: object) -> bool:
  """Compare a bare name by value."""
  eop_match(LIMIT, value)


@implicit_return()
def match_reads_local_in_guard(value: object, floor: int) -> bool:
  """Read the function's own locals from a guard."""
  eop_match(eop_when(eop_var.v, eop_var.v > floor), value)


# ---------------------------------------------------------------- eop_case


@implicit_return()
def describe(shape: object) -> str:
  """Hoisted path: the call is the whole tail expression."""
  eop_case(
    shape,
    eop_clause(eop_when(Point(0, eop_var.y), eop_var.y > 0), f'above the origin at {eop_var.y}'),
    eop_clause(Point(eop_var.x, 0), f'on the x axis at {eop_var.x}'),
    eop_clause(Circle(eop_var.r), f'circle of radius {eop_var.r}'),
    default='elsewhere',
  )


@implicit_return()
def describe_assigned(shape: object) -> str:
  """Hoisted path through an assignment."""
  label: str = eop_case(shape, eop_clause(Point(eop_var.x, eop_var.y), 'point'), default='other')
  f'<{label}>'


@implicit_return()
def describe_all(shapes: list[object]) -> list[str]:
  """Matcher path: the call sits inside a comprehension."""
  [
    eop_case(
      s,
      eop_clause(eop_when(Point(0, eop_var.y), eop_var.y > 0), f'above the origin at {eop_var.y}'),
      eop_clause(Point(eop_var.x, 0), f'on the x axis at {eop_var.x}'),
      eop_clause(Circle(eop_var.r), f'circle of radius {eop_var.r}'),
      default='elsewhere',
    )
    for s in shapes
  ]


@implicit_return()
def case_in_operand(shape: object) -> str:
  """Matcher path as a concatenation operand."""
  'shape: ' + eop_case(
    shape, eop_clause(Point(eop_var.x, eop_var._), f'x={eop_var.x}'), default='?'
  )


@implicit_return()
def lazy_case(value: object) -> str:
  """Only the selected value and the subject run once; the call log proves it."""
  eop_case(
    note('subject', value),
    eop_clause(1, note('v1', 'one')),
    eop_clause(2, note('v2', 'two')),
    default=note('d', 'other'),
  )


@implicit_return()
def lazy_case_matchers(values: list[object]) -> list[str]:
  """Show that the matcher path is lazy too."""
  [
    eop_case(note('subject', v), eop_clause(1, note('v1', 'one')), default=note('d', 'other'))
    for v in values
  ]


@implicit_return()
def case_sequence(value: object) -> str:
  """Sequence patterns with a star."""
  eop_case(
    value,
    eop_clause([], 'empty'),
    eop_clause([eop_var.first], f'one: {eop_var.first}'),
    eop_clause([eop_var.first, *eop_var.rest], f'{eop_var.first} then {len(eop_var.rest)}'),
    default='not a sequence',
  )


@implicit_return()
def case_mapping(value: object) -> str:
  """Match mapping patterns with a rest capture."""
  eop_case(
    value,
    eop_clause({'id': eop_var.i, **eop_var.rest}, f'{eop_var.i} + {sorted(eop_var.rest)}'),
    eop_clause({}, 'any mapping'),
    default='not a mapping',
  )


@implicit_return()
def case_values(value: object) -> str:
  """Literal, negative, singleton, dotted and bare-name patterns."""
  eop_case(
    value,
    eop_clause(0, 'zero'),
    eop_clause(-1, 'minus one'),
    eop_clause(None, 'none'),
    eop_clause(True, 'true'),
    eop_clause('text', 'text'),
    eop_clause(Color.RED, 'red'),
    eop_clause(LIMIT, 'limit'),
    default='other',
  )


@implicit_return()
def case_values_matchers(values: list[object]) -> list[str]:
  """Run the same patterns through the matcher path."""
  [
    eop_case(
      v,
      eop_clause(0, 'zero'),
      eop_clause(-1, 'minus one'),
      eop_clause(None, 'none'),
      eop_clause(True, 'true'),
      eop_clause('text', 'text'),
      eop_clause(Color.RED, 'red'),
      eop_clause(LIMIT, 'limit'),
      default='other',
    )
    for v in values
  ]


@implicit_return()
def case_keyword_class(value: object) -> str:
  """Keyword class patterns and nesting."""
  eop_case(
    value,
    eop_clause(Point(x=0, y=eop_var.y), f'y={eop_var.y}'),
    eop_clause(
      [Point(eop_var.a, eop_var._), Point(eop_var.b, eop_var._)], f'{eop_var.a}-{eop_var.b}'
    ),
    default='other',
  )


@implicit_return()
def case_guard_rules(value: object) -> str:
  """Guards: exactly ``True`` passes, truthy does not, raising counts as no match."""
  eop_case(
    value,
    eop_clause(eop_when(eop_var.v, eop_var.v.missing > 1), 'raised'),
    eop_clause(eop_when(eop_var.v, eop_var.v), 'truthy'),
    eop_clause(eop_when(eop_var.v, eop_var.v == 3), 'three'),
    default='fell through',
  )


@implicit_return()
def case_guard_rules_matchers(values: list[object]) -> list[str]:
  """Run the same guards through the matcher path."""
  [
    eop_case(
      v,
      eop_clause(eop_when(eop_var.v, eop_var.v.missing > 1), 'raised'),
      eop_clause(eop_when(eop_var.v, eop_var.v), 'truthy'),
      eop_clause(eop_when(eop_var.v, eop_var.v == 3), 'three'),
      default='fell through',
    )
    for v in values
  ]


@implicit_return()
def case_captures_private(shape: object) -> tuple[str, str]:
  """Show that a capture never leaks into the function's locals."""
  y = 'untouched'
  label = eop_case(shape, eop_clause(Point(0, eop_var.y), 'axis'), default='other')
  (label, y)  # noqa: B018 - implicit return


@implicit_return()
def case_nested_forms(shape: object) -> str:
  """Forms nested inside clause values and the subject."""
  eop_case(
    eop_cond(eop_clause(shape is None, Point(0, 0)), default=shape),
    eop_clause(
      Point(eop_var.x, eop_var.y),
      eop_cond(eop_clause(eop_var.x == eop_var.y, 'diagonal'), default='off diagonal'),
    ),
    default='not a point',
  )


@implicit_return()
def case_in_branch(flag: bool, shape: object) -> str:
  """Place a hoisted ``match`` inside an ``if`` branch."""
  if flag:
    eop_case(shape, eop_clause(Point(eop_var.x, eop_var._), f'x {eop_var.x}'), default='?')
  else:
    'skipped'


@implicit_return()
async def async_case(shape: object) -> str:
  """``eop_case`` in a coroutine function, matcher path with ``await`` in a value."""
  'got ' + eop_case(shape, eop_clause(Point(eop_var.x, eop_var._), str(eop_var.x)), default='?')


@implicit_return()
def case_subject_once(values: deque[int]) -> str:
  """Run the subject expression once in the matcher path."""
  f'{eop_case(values.popleft(), eop_clause(1, "one"), eop_clause(2, "two"), default="other")}!'


@guarded_expression(implicit_return=False)
def explicit_case(shape: object) -> str:
  """``eop_case`` in explicit-return mode keeps the explicit return."""
  label = eop_case(shape, eop_clause(Point(eop_var.x, eop_var._), f'x={eop_var.x}'), default='?')
  return label.upper()


# ---------------------------------------------------------------- handwritten oracles


def oracle_describe(shape: object) -> str:
  """Return what ``describe`` must return, as a real ``match``."""
  match shape:
    case Point(0, y) if y > 0:
      result = f'above the origin at {y}'
    case Point(x, 0):
      result = f'on the x axis at {x}'
    case Circle(r):
      result = f'circle of radius {r}'
    case _:
      result = 'elsewhere'
  return result


def oracle_sequence(value: object) -> str:
  """Return what ``case_sequence`` must return."""
  match value:
    case []:
      result = 'empty'
    case [first]:
      result = f'one: {first}'
    case [first, *rest]:
      result = f'{first} then {len(rest)}'
    case _:
      result = 'not a sequence'
  return result


def oracle_mapping(value: object) -> str:
  """Return what ``case_mapping`` must return."""
  match value:
    case {'id': i, **rest}:
      result = f'{i} + {sorted(rest)}'
    case {}:
      result = 'any mapping'
    case _:
      result = 'not a mapping'
  return result


def oracle_values(value: object) -> str:
  """Return what ``case_values`` must return."""
  match value:
    case 0:
      result = 'zero'
    case -1:
      result = 'minus one'
    case None:
      result = 'none'
    case True:
      result = 'true'
    case 'text':
      result = 'text'
    case Color.RED:
      result = 'red'
    case v if v == LIMIT:
      result = 'limit'
    case _:
      result = 'other'
  return result


def oracle_keyword_class(value: object) -> str:
  """Return what ``case_keyword_class`` must return."""
  match value:
    case Point(x=0, y=y):
      result = f'y={y}'
    case [Point(a, _), Point(b, _)]:
      result = f'{a}-{b}'
    case _:
      result = 'other'
  return result
