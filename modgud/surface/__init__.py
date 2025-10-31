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
from .handlers.guarded_expression_handler import guarded_expression
from .services.common_guard_service import CommonGuards
from .services.guard_registry_service import GuardRegistry

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
