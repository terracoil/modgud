"""Guarded Expression - Unified decorator combining guard clauses with implicit return.

This package provides the primary interface for the modgud library, unifying
guard clause validation and implicit return transformation into a single decorator.
"""

from .common_guards import CommonGuards
from .guard_registry import (
  get_guard,
  get_registry,
  has_custom_guard,
  list_custom_guards,
  list_guard_namespaces,
  register_guard,
  unregister_guard,
)
from .guarded_expression import guarded_expression

__all__ = [
  'guarded_expression',
  'CommonGuards',
  'register_guard',
  'get_guard',
  'has_custom_guard',
  'list_custom_guards',
  'list_guard_namespaces',
  'unregister_guard',
  'get_registry',
]
