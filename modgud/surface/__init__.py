"""
Surface layer - Public API and orchestration.

Implements the public decorator API using infrastructure services.
"""

from ..infrastructure import (
  ExplicitReturnDisallowedError,
  GuardClauseError,
  ImplicitReturnError,
  MissingImplicitReturnError,
  UnsupportedConstructError,
)
from .common_guards import CommonGuards
from .decorator import guarded_expression
from .registry import GuardRegistry

__all__ = [
  # Main decorator
  'guarded_expression',
  # Validators
  'CommonGuards',
  # Registry
  'GuardRegistry',
  # Error classes (re-exported from infrastructure)
  'GuardClauseError',
  'ImplicitReturnError',
  'ExplicitReturnDisallowedError',
  'MissingImplicitReturnError',
  'UnsupportedConstructError',
]
