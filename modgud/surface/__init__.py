"""
Surface layer - Public API and orchestration.

Implements the public decorator API using infrastructure services.
"""

from .decorator import guarded_expression
from .registry import GuardRegistry
from .validators import CommonGuards

__all__ = [
  # Main decorator
  'guarded_expression',
  # Validators
  'CommonGuards',
  # Registry
  'GuardRegistry',
]
