"""Guarded-expression domain: enum, errors, ports."""

from .enums import GuardFailureStrategy
from .errors import GuardClauseError

__all__ = [
  'GuardClauseError',
  'GuardFailureStrategy',
]
