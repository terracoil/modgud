"""Modgud - Modern Guard Clauses for Python.

A library for implementing guard clause decorators with single return point architecture.

Primary API:
  - guarded_expression: Unified decorator combining guards + implicit return
  - CommonGuards: Pre-built guard validators
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
