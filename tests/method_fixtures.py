"""Module-level classes for the method-decoration tests.

They live here, not inside test functions, because the implicit-return rewrite reads the
source from disk; see ``tests/test_method_decoration.py`` for what each shape proves.
"""

from __future__ import annotations

from typing import Any

from modgud import GuardFailureEnum, Guards, guarded_expression, implicit_return

POSITIVE = Guards.positive('x')


def explain(errors: list[str], *args: Any, **kwargs: Any) -> dict[str, Any]:
  """CALL_HANDLER handler that records exactly what it was given."""
  return {'errors': errors, 'args': args, 'kwargs': kwargs}


class Calculator:
  """Every method shape the decorators support, one method each."""

  __secret: int = 7  # name-mangled: becomes _Calculator__secret
  factor: int = 3

  def __init__(self, base: int = 0) -> None:
    """Keep a base value so instance methods have state to read."""
    self.base: int = base

  @guarded_expression(POSITIVE)
  def double(self, x: int) -> int:
    """Double x."""
    x * 2

  @guarded_expression(POSITIVE)
  def add_base(self, x):
    self.base + x

  @guarded_expression(lambda x: x % 2 == 0 or 'x must be even')
  def half(self, x):
    x // 2

  @classmethod
  @guarded_expression(POSITIVE)
  def scale(cls, x):
    cls.factor * x

  @guarded_expression(POSITIVE)
  @classmethod
  def scale_inner(cls, x):
    cls.factor * x

  @staticmethod
  @guarded_expression(POSITIVE)
  def square(x):
    x * x

  @guarded_expression(POSITIVE)
  @staticmethod
  def square_inner(x):
    x * x

  @guarded_expression(POSITIVE)
  async def double_async(self, x):
    x * 2

  @guarded_expression(POSITIVE, implicit_return=False)
  def explicit(self, x):
    return x + self.base

  @guarded_expression(POSITIVE, implicit_return=False)
  @implicit_return()
  def stacked(self, x):
    x - self.base

  @implicit_return()
  def classify(self, x):
    if x > 0:
      'positive'
    else:
      'non-positive'

  @implicit_return()
  def secret(self):
    self.__secret  # noqa: B018 - implicit return

  @guarded_expression(POSITIVE, strategy=GuardFailureEnum.CALL_HANDLER, on_failure=explain)
  def handled(self, x):
    x  # noqa: B018 - implicit return

  @implicit_return()
  def by_own_name(self, x):
    Calculator(x).base + Calculator.factor

  @implicit_return()
  def clamp(self, x=factor):
    x if x < Calculator.factor else Calculator.factor  # noqa: B018 - implicit return


def not_a_method(cls, n):
  """Multiply; a module-level function whose first parameter happens to be called ``cls``."""
  return cls * n


guarded_not_a_method = guarded_expression(Guards.positive('cls'), implicit_return=False)(
  not_a_method
)


# The README quick start, verbatim.
class DiscountCalculator:
  @staticmethod
  @guarded_expression(
    Guards.positive('x'),
    Guards.in_range(1, 100, 'x'),
  )
  def calculate(x):
    if x >= 50:
      x * 0.2
    else:
      x * 0.1


class DiscountCalculatorV2:
  @staticmethod
  @guarded_expression(
    Guards.positive('x'),
    Guards.in_range(1, 100, 'x'),
    implicit_return=False,
  )
  @implicit_return()
  def calculate(x):
    if x >= 50:
      x * 0.2
    else:
      x * 0.1
