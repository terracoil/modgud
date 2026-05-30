"""Domain layer aggregator.

Re-exports the public-facing types from each feature subpackage so callers
can use the shortest absolute path (`from modgud.domain import X`).
"""

from .guarded_expr import GuardClauseError, GuardFailureStrategy
from .implicit_ret import (
  ExplicitReturnDisallowedError,
  ImplicitReturnError,
  MissingImplicitReturnError,
  UnsupportedConstructError,
)

__all__ = [
  'ExplicitReturnDisallowedError',
  'GuardClauseError',
  'GuardFailureStrategy',
  'ImplicitReturnError',
  'MissingImplicitReturnError',
  'UnsupportedConstructError',
]
