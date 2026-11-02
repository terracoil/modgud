"""Instance, static and class methods, with modgud on either side of the built-in decorator.

A method may name its own class and keep a class-attribute default; it may not use
zero-argument ``super()`` or ``__class__`` (there is no cell for them after the rewrite),
and ``@implicit_return()`` may not go above a guarded method.

Run: poetry run python examples/classy/10_decorator_composition.py
See: docs/api-reference.md#methods
"""

from __future__ import annotations

import inspect
from typing import ClassVar

from modgud import CommonGuards, UnsupportedConstructError, guarded_expression, implicit_return


class Thermostat:
  """Every method shape modgud decorates, plus the refusals (applied in ``demo``)."""

  STEP: ClassVar[int] = 2

  def __init__(self, target: int = 20) -> None:
    """Start at ``target`` degrees Celsius."""
    self.target: int = target

  @guarded_expression(CommonGuards.positive('by'))  # the guard sees ``by``, never ``self``
  def warmer(self, by: int) -> int:
    """Return the target raised by ``by`` degrees."""
    self.target + by

  @staticmethod  # built-in outermost
  @guarded_expression(CommonGuards.in_range(-50, 100, 'celsius'))
  def to_fahrenheit(celsius: float) -> float:
    """Convert ``celsius`` to Fahrenheit."""
    celsius * 9 / 5 + 32

  @guarded_expression(CommonGuards.in_range(-58, 212, 'fahrenheit'))  # modgud outermost
  @staticmethod
  def to_celsius(fahrenheit: float) -> float:
    """Convert ``fahrenheit`` to Celsius."""
    (fahrenheit - 32) * 5 / 9

  @classmethod
  @guarded_expression(CommonGuards.matches_pattern(r'^(eco|comfort)$', 'mode'))
  def preset(cls, mode: str) -> Thermostat:
    """Build a thermostat for a named ``mode``."""
    cls(18 if mode == 'eco' else 21)

  def no_zero_arg_super(self) -> str:
    """Don't: zero-argument ``super()``; use ``super(Thermostat, self)`` instead."""
    super().__repr__()

  @implicit_return()
  def nudge(self, step: int = STEP) -> int:
    """Return the target plus ``step``; the class-attribute default is kept as is."""
    self.target + step

  @classmethod
  def demo(cls) -> None:
    """Call every shape (a guard that saw ``self`` would blow up), then show both refusals."""
    assert cls(20).warmer(3) == 23 and cls.to_fahrenheit(100) == 212
    assert cls.to_celsius(212) == 100 and cls.preset('eco').target == 18
    assert isinstance(inspect.getattr_static(cls, 'to_celsius'), staticmethod)
    assert cls.warmer.__qualname__ == 'Thermostat.warmer'
    assert cls(20).nudge() == 22 and Thermostat(20).nudge(5) == 25

    refused: str = ''
    try:
      implicit_return()(cls.no_zero_arg_super)
    except UnsupportedConstructError as error:
      refused = error.msg
    assert 'super()' in refused

    stacking: str = ''
    try:
      implicit_return()(cls.warmer)  # above a guarded method, the rewrite would drop the guard
    except TypeError as error:
      stacking = str(error)
    assert stacking.startswith('@implicit_return() must sit below @guarded_expression')

    print(f'warmer(3) = {cls(20).warmer(3)}, to_fahrenheit(100) = {cls.to_fahrenheit(100)}')
    print('refused at decoration:', refused, '|', stacking)


if __name__ == '__main__':
  Thermostat.demo()
