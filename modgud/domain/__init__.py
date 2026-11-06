"""Domain layer: re-exports the passive types, enum, errors and ports.

Modules inside ``modgud`` import from the owning feature package, never from this facade.
"""

from .guarded_expr import GuardClauseError, GuardFailureEnum, GuardFunction, GuardPort
from .implicit_ret import (
  ExplicitReturnDisallowedError,
  ImplicitReturnError,
  ImplicitReturnPort,
  MissingImplicitReturnError,
  UnsupportedConstructError,
)

__all__ = [
  'ExplicitReturnDisallowedError',
  'GuardClauseError',
  'GuardFailureEnum',
  'GuardFunction',
  'GuardPort',
  'ImplicitReturnError',
  'ImplicitReturnPort',
  'MissingImplicitReturnError',
  'UnsupportedConstructError',
]
