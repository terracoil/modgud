"""Guarded-expression domain: enum, errors, ports."""

from .enums import GuardFailureStrategy
from .errors import GuardClauseError
from .types import GuardFunction

__all__ = [
  'GuardClauseError',
  'GuardFailureStrategy',
  'GuardFunction',
]
