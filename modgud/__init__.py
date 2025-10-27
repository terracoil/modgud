"""Modgud - Modern Guard Clauses for Python.

A library for implementing guard clause decorators with single return point architecture.

Primary API:
  - guarded_expression: Unified decorator combining guards + implicit return
  - CommonGuards: Pre-built guard validators

Usage Examples:

    Basic guard validation:
        from modgud import guarded_expression, CommonGuards

        @guarded_expression(
            CommonGuards.positive("x"),
            CommonGuards.type_check(int, "x")
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
        from modgud import register_guard

        def valid_email(param_name="email", position=0):
            def check(*args, **kwargs):
                value = kwargs.get(param_name, args[position] if position < len(args) else None)
                return "@" in str(value) or f"{param_name} must be a valid email"
            return check

        register_guard("valid_email", valid_email, namespace="validators")
"""

from .guarded_expression import CommonGuards, guarded_expression
from .guarded_expression.errors import (
  ExplicitReturnDisallowedError,
  GuardClauseError,
  ImplicitReturnError,
  MissingImplicitReturnError,
  UnsupportedConstructError,
)
from .guarded_expression.guard_registry import (
  get_guard,
  get_registry,
  has_custom_guard,
  list_custom_guards,
  list_guard_namespaces,
  register_guard,
  unregister_guard,
)

__version__ = '0.2.0'
__all__ = [
  'guarded_expression',
  'CommonGuards',
  'GuardClauseError',
  'ImplicitReturnError',
  'ExplicitReturnDisallowedError',
  'MissingImplicitReturnError',
  'UnsupportedConstructError',
  'register_guard',
  'get_guard',
  'has_custom_guard',
  'list_custom_guards',
  'list_guard_namespaces',
  'unregister_guard',
  'get_registry',
]
