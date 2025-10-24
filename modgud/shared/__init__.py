"""Shared types and errors for the modgud library."""

from .errors import (
  ExplicitReturnDisallowedError,
  GuardClauseError,
  ImplicitReturnError,
  MissingImplicitReturnError,
  UnsupportedConstructError,
)
from .types import FailureBehavior, FailureTypes, GuardFunction

__all__ = [
  'GuardFunction',
  'FailureBehavior',
  'FailureTypes',
  'GuardClauseError',
  'ImplicitReturnError',
  'ExplicitReturnDisallowedError',
  'MissingImplicitReturnError',
  'UnsupportedConstructError',
]
