"""Domain layer: re-exports the passive types, enum, errors and ports.

Modules inside ``modgud`` import from the owning subpackage, never from this facade.
"""

from .enums import GuardFailureEnum
from .errors import (
  ExplicitReturnDisallowedError,
  GuardClauseError,
  ImplicitReturnError,
  MarkerNotRewrittenError,
  MarkerPlacementError,
  MarkerUsageError,
  MissingImplicitReturnError,
  UnsupportedConstructError,
)
from .ports import EopPort, GuardPort, ImplicitReturnPort
from .types import GuardFunction, eop_clause

__all__ = [
  'EopPort',
  'ExplicitReturnDisallowedError',
  'GuardClauseError',
  'GuardFailureEnum',
  'GuardFunction',
  'GuardPort',
  'ImplicitReturnError',
  'ImplicitReturnPort',
  'MarkerNotRewrittenError',
  'MarkerPlacementError',
  'MarkerUsageError',
  'MissingImplicitReturnError',
  'UnsupportedConstructError',
  'eop_clause',
]
