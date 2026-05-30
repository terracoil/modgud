"""Modgud - guard clauses + implicit returns for Python.

Primary surface:

- ``guarded_expression`` - unified decorator combining guard validation
  with optional implicit-return AST rewrite. Failure dispatch is controlled
  by ``GuardFailureStrategy`` plus a paired ``on_failure`` payload; the
  ``continuance`` parameter caps how many guards past the first failure
  are still evaluated.
- ``implicit_return`` - standalone Ruby-style implicit-return decorator.
- Pre-built guard validators: ``positive``, ``not_none``, ``not_empty``,
  ``type_check``, ``in_range``, ``matches_pattern``, ``valid_file_path``,
  ``valid_url``, ``valid_enum``.
- ``GuardRegistry`` for custom guard registration.

Example::

    from modgud import (
      guarded_expression,
      GuardFailureStrategy,
      positive,
      GuardClauseError,
    )


    @guarded_expression(positive('x'))
    def double(x):
      x * 2  # implicit return


    @guarded_expression(
      positive('x'),
      strategy=GuardFailureStrategy.RETURN_VALUE,
      on_failure=-1,
    )
    def safe_square(x):
      x * x


    # Collect up to two extra failures past the first:
    @guarded_expression(
      positive('x'),
      positive('y'),
      continuance=2,
    )
    def add(x, y):
      x + y
"""

from .app import guarded_expression, implicit_return
from .domain import (
  ExplicitReturnDisallowedError,
  GuardClauseError,
  GuardFailureStrategy,
  ImplicitReturnError,
  MissingImplicitReturnError,
  UnsupportedConstructError,
)
from .infrastructure import CommonGuards, GuardRegistry

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

__version__ = '2.0.0'
__all__ = [
  # Primary decorators
  'guarded_expression',
  'implicit_return',
  # Strategy enum
  'GuardFailureStrategy',
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
