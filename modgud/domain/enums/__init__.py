"""
Domain enums for modgud.

Enumeration classes for domain concepts following domain-driven design
principles. The domain layer is passive and contains no business logic
- only enumeration definitions.

This module re-exports enum definitions from their individual files
following the single class per file principle.
"""

from .failure_strategy import FailureStrategy
from .guard_strategy import GuardStrategy
from .service_lifetime import ServiceLifetime

__all__ = [
  'FailureStrategy',
  'GuardStrategy',
  'ServiceLifetime',
]