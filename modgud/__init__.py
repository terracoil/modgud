"""
Modgud - Modern Guard Clauses for Python.

A library for implementing guard clause decorators with single return point architecture.

Primary API:
  - guarded_expression: Unified decorator combining guards + implicit return
  - Pre-built guard validators: positive, not_none, not_empty, type_check, etc.

Usage Examples:

    Basic guard validation:
        from modgud import guarded_expression, positive, type_check

        @guarded_expression(
            positive("x"),
            type_check(int, "x"),
            implicit_return=False
        )
        def calculate(x):
            return x * 2

    Implicit return (Ruby-style):
        @guarded_expression()
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

from .domain.errors import (
  ExplicitReturnDisallowedError,
  GuardClauseError,
  ImplicitReturnError,
  MissingImplicitReturnError,
  UnsupportedConstructError,
)
from .surface.decorator import guarded_expression
from .surface.registry import GuardRegistry
from .surface.validators import CommonGuards

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

__version__ = '1.1.0'
__all__ = [
  # Primary decorator
  'guarded_expression',
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
