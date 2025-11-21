"""
Modgud - Modern Guard Clauses for Python.

A library for implementing guard clause decorators with single return point architecture.

Primary API:
  - guarded_expression: Unified decorator combining guards + implicit return
  - implicit_return: Standalone decorator for Ruby-style implicit returns
  - Pre-built guard validators: positive, not_none, not_empty, type_check, etc.

Usage Examples:

    Basic guard validation (explicit return):
        from modgud import guarded_expression, positive, type_check

        @guarded_expression(
            positive("x"),
            type_check(int, "x"),
            implicit_return=False
        )
        def calculate(x):
            return x * 2

    Implicit return with guards (recommended approach):
        from modgud import implicit_return, guarded_expression, positive

        @implicit_return
        @guarded_expression(positive("x"))
        def process(x):
            result = x * 2
            result  # Implicit return

    Standalone implicit return (Ruby-style):
        from modgud import implicit_return

        @implicit_return
        def process(x, y):
            if x > y:
                x + y  # Implicit return
            else:
                x - y  # Implicit return

    Custom guard registration:
        from modgud import GuardRegistry

        def valid_email(param_name="email", position=0):
            def check(*args, **kwargs):
                value = kwargs.get(param_name, args[position] if position < len(args) else None)
                return "@" in str(value) or f"{param_name} must be a valid email"
            return check

        GuardRegistry.register("valid_email", valid_email, namespace="validators")
"""

from .app.decorator.guarded_expression import guarded_expression
from .app.decorator.implicit_return_decorator import implicit_return
from .app.decorator.inject_decorator import Inject
from .app.decorator.pipeable import pipeable
from .domain.exceptions import (
  ExplicitReturnDisallowedError,
  GuardClauseError,
  ImplicitReturnError,
  MissingImplicitReturnError,
  UnsupportedConstructError,
)
from .infrastructure.chainable_expression import ChainableExpression
from .infrastructure.chained_expression_factory import ChainedExpressionFactory
from .infrastructure.common_guards import CommonGuards
from .infrastructure.err_result import Err
from .infrastructure.guard_registry import GuardRegistry
from .infrastructure.maybe_factory import MaybeFactory
from .infrastructure.nothing_maybe import Nothing
from .infrastructure.ok_result import Ok
from .infrastructure.result_factory import ResultFactory
from .infrastructure.safe_expression_factory import SafeExpressionFactory
from .infrastructure.some_maybe import Some

# Export guards as module-level functions for convenient direct import
not_empty = CommonGuards.not_empty
not_none = CommonGuards.not_none
positive = CommonGuards.positive
in_range = CommonGuards.in_range
type_check = CommonGuards.type_check
matches_pattern = CommonGuards.matches_pattern
valid_file_path = CommonGuards.valid_file_path
valid_url = CommonGuards.valid_url
valid_enum = CommonGuards.valid_enum

# Create factory instances
_safe_factory = SafeExpressionFactory()
_chained_factory = ChainedExpressionFactory()

# Export factory functions for convenient direct import
safe_expression = _safe_factory.create_decorator
chained_expression = _chained_factory.create_decorator
# pipeable is already imported from app.decorator.pipeable above
chain = _chained_factory.create_expression

# Export factory functions for monadic types
Maybe = MaybeFactory
Result = ResultFactory

__version__ = '1.2.0'
__all__ = [
  # Primary decorators
  'guarded_expression',
  'implicit_return',
  'pipeable',
  'safe_expression',
  'chained_expression',
  'Inject',
  # Monadic types and factories
  'Maybe',
  'Some',
  'Nothing',
  'Result',
  'Ok',
  'Err',
  'ChainableExpression',
  'chain',
  # Classes
  'CommonGuards',
  'GuardRegistry',
  # Guard validators (convenience exports)
  'not_empty',
  'not_none',
  'positive',
  'in_range',
  'type_check',
  'matches_pattern',
  'valid_file_path',
  'valid_url',
  'valid_enum',
  # Error classes
  'GuardClauseError',
  'ImplicitReturnError',
  'ExplicitReturnDisallowedError',
  'MissingImplicitReturnError',
  'UnsupportedConstructError',
]
