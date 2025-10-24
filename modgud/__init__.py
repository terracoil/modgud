"""Modgud - Modern Guard Clauses for Python.

A library for implementing guard clause decorators with single return point architecture.

Primary API:
  - guarded_expression: Unified decorator combining guards + implicit return
  - CommonGuards: Pre-built guard validators
"""

from .guarded_expression import CommonGuards, guarded_expression
from .shared.errors import (
  ExplicitReturnDisallowedError,
  GuardClauseError,
  ImplicitReturnError,
  MissingImplicitReturnError,
  UnsupportedConstructError,
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
]
