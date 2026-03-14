"""Domain enums for modgud.

Enumeration classes for domain concepts following domain-driven design
principles. The domain layer is passive and contains no business logic
- only enumeration definitions.

This module re-exports enum definitions from their individual files
following the single class per file principle.
"""

from .failure_strategy import FailureStrategy
from .guard_strategy import GuardStrategy
from .info_message_enum import InfoMessageEnum

__all__ = [
  'FailureStrategy',
  'GuardStrategy',
  'InfoMessageEnum',
]
