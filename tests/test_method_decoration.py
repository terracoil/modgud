"""Decorating methods: instance, static, class and async, in every decoration form."""

from __future__ import annotations

import asyncio
import inspect

import pytest
from modgud import GuardClauseError, UnsupportedConstructError, implicit_return

from tests.method_fixtures import (
  Calculator,
  DiscountCalculator,
  DiscountCalculatorV2,
  guarded_not_a_method,
)


class TestInstanceMethods:
  def test_guard_checks_the_named_parameter_not_self(self):
    assert Calculator(-5).double(4) == 8  # a negative base must not trip positive('x')
    assert Calculator(-5).add_base(4) == -1

  def test_positional_and_keyword_calls_agree(self):
    calc = Calculator(1)
    assert calc.double(4) == calc.double(x=4) == 8
    assert Calculator.double(calc, 4) == 8
    assert Calculator.double(self=calc, x=4) == 8

  def test_guard_failure_raises(self):
    with pytest.raises(GuardClauseError, match='x must be positive'):
      Calculator().double(-1)
    with pytest.raises(GuardClauseError, match='x must be positive'):
      Calculator().double(x=0)

  def test_custom_guards_see_arguments_without_the_receiver(self):
    assert Calculator().half(8) == 4
    with pytest.raises(GuardClauseError, match='x must be even'):
      Calculator().half(7)

  def test_explicit_return_mode(self):
    assert Calculator(10).explicit(4) == 14
    with pytest.raises(GuardClauseError):
      Calculator(10).explicit(-4)

  def test_stacked_decorators(self):
    assert Calculator(1).stacked(4) == 3
    with pytest.raises(GuardClauseError):
      Calculator(1).stacked(-4)

  def test_implicit_return_alone(self):
    assert Calculator().classify(1) == 'positive'
    assert Calculator().classify(-1) == 'non-positive'

  def test_async_method(self):
    assert asyncio.run(Calculator().double_async(4)) == 8
    with pytest.raises(GuardClauseError):
      asyncio.run(Calculator().double_async(-4))

  def test_call_handler_receives_the_full_argument_list(self):
    calc = Calculator()
    outcome = calc.handled(-1)
    assert outcome == {'errors': ['x must be positive'], 'args': (calc, -1), 'kwargs': {}}


class TestClassAndStaticMethods:
  def test_classmethod_outside_modgud(self):
    assert Calculator.scale(2) == 6
    assert Calculator().scale(x=2) == 6
    with pytest.raises(GuardClauseError):
      Calculator.scale(-2)

  def test_classmethod_inside_modgud(self):
    assert isinstance(inspect.getattr_static(Calculator, 'scale_inner'), classmethod)
    assert Calculator.scale_inner(2) == 6
    with pytest.raises(GuardClauseError):
      Calculator.scale_inner(-2)

  def test_staticmethod_outside_modgud(self):
    assert Calculator.square(3) == 9
    assert Calculator().square(3) == 9
    with pytest.raises(GuardClauseError):
      Calculator.square(-3)

  def test_staticmethod_inside_modgud(self):
    assert isinstance(inspect.getattr_static(Calculator, 'square_inner'), staticmethod)
    assert Calculator.square_inner(3) == 9
    with pytest.raises(GuardClauseError):
      Calculator.square_inner(-3)


class TestClassContext:
  def test_name_mangled_attributes_resolve(self):
    assert Calculator().secret() == 7

  def test_a_method_can_name_its_own_class(self):
    assert Calculator().by_own_name(4) == 7

  def test_metadata_is_preserved(self):
    method = Calculator.double
    assert method.__name__ == 'double'
    assert method.__qualname__ == 'Calculator.double'
    assert method.__doc__ == 'Double x.'
    assert list(inspect.signature(method).parameters) == ['self', 'x']
    assert method.__annotations__ == {'x': 'int', 'return': 'int'}  # postponed annotations
    assert Calculator.scale.__qualname__ == 'Calculator.scale'

  def test_zero_argument_super_is_refused_at_decoration_time(self):
    class Base:
      def who(self) -> str:
        return 'base'

    with pytest.raises(UnsupportedConstructError, match='Zero-argument super'):

      class Child(Base):
        @implicit_return()
        def who(self):
          super().who() + '+child'

  def test_class_scope_default_is_kept(self):
    assert Calculator().clamp() == 3
    assert Calculator().clamp(1) == 1

  def test_explicit_dunder_class_is_refused_at_decoration_time(self):
    with pytest.raises(UnsupportedConstructError, match='__class__'):

      class Peeking:
        @implicit_return()
        def me(self):
          __class__  # noqa: B018 - implicit return

  def test_a_nested_class_may_use_zero_argument_super(self):
    class Helper:
      @implicit_return()
      def build(self):
        class Inner(dict):
          def __init__(self) -> None:
            super().__init__(ok=True)

        Inner()

    assert Helper().build() == {'ok': True}

  def test_receiver_skipping_needs_a_real_method(self):
    with pytest.raises(GuardClauseError, match='cls must be positive'):
      guarded_not_a_method(-1, 5)
    assert guarded_not_a_method(2, 5) == 10


class TestReadmeQuickStart:
  @pytest.mark.parametrize('calculator', [DiscountCalculator, DiscountCalculatorV2])
  def test_the_readme_example_as_written(self, calculator):
    assert calculator.calculate(75) == 15.0
    assert calculator.calculate(25) == 2.5
    with pytest.raises(GuardClauseError):
      calculator.calculate(-10)
