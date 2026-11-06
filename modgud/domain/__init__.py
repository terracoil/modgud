"""Domain layer: re-exports the passive types, enum, errors and ports.

Modules inside ``modgud`` import from the owning subpackage, never from this facade.
"""

from .enums import GuardFailureEnum
from .errors import (
  ExplicitReturnDisallowedError,
  GuardClauseError,
  ImplicitReturnError,
  MissingImplicitReturnError,
  UnsupportedConstructError,
)
from .ports import GuardPort, ImplicitReturnPort
from .types import GuardFunction

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
