"""
Guarded Expression - Unified decorator combining guard clauses with implicit return.

This package provides the primary interface for the modgud library, unifying
guard clause validation and implicit return transformation into a single decorator.
"""

from .common_guards import CommonGuards
from .guard_registry import GuardRegistry
from .guarded_expression import guarded_expression

__all__ = [
  'guarded_expression',
  'CommonGuards',
  'GuardRegistry',
]
