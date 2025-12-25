"""
GuardStrategy enum for modgud domain layer.

Enumeration for guard evaluation strategies following domain-driven design
principles. The domain layer is passive and contains no business logic
- only enumeration definitions.
"""

from enum import Enum, auto

__all__ = ['GuardStrategy']


class GuardStrategy(Enum):
  """Strategy for how guards should be evaluated."""

  FAIL_FAST = auto()  # Stop on first guard failure
  COLLECT_ALL = auto()  # Evaluate all guards and collect failures
  WARN_ONLY = auto()  # Log warnings but don't fail
