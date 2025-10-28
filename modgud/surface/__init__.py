"""
Surface layer - Public API and orchestration.

Implements the public decorator API using infrastructure services.
"""

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
]
