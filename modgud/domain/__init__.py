"""Domain layer: re-exports the passive types, enum and errors.

Ports are deliberately not re-exported here: import them from ``modgud`` or from
``modgud.domain.<feature>.ports``. Modules inside ``modgud`` import from the owning
feature package, never from this facade.
"""

from modgud.domain.guarded_expr import GuardClauseError, GuardFailureEnum, GuardFunction
from modgud.domain.implicit_ret import (
  ExplicitReturnDisallowedError,
  ImplicitReturnError,
  MissingImplicitReturnError,
  UnsupportedConstructError,
)

__all__ = [
  'ExplicitReturnDisallowedError',
  'GuardClauseError',
  'GuardFailureEnum',
  'GuardFunction',
  'ImplicitReturnError',
  'MissingImplicitReturnError',
  'UnsupportedConstructError',
]
