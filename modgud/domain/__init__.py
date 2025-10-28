"""
Domain layer - Core types, errors, messages, and ports.

Ports are in domain.ports subpackage and define contracts for
infrastructure implementations.
"""

from .errors import (
  ExplicitReturnDisallowedError,
  GuardClauseError,
  ImplicitReturnError,
  MissingImplicitReturnError,
  UnsupportedConstructError,
)
from .messages import ErrorMessages, InfoMessages
from .types import FailureBehavior, GuardFunction

__all__ = [
  # Types
  'GuardFunction',
  'FailureBehavior',
  # Errors
  'GuardClauseError',
  'ImplicitReturnError',
  'ExplicitReturnDisallowedError',
  'MissingImplicitReturnError',
  'UnsupportedConstructError',
  # Messages
  'ErrorMessages',
  'InfoMessages',
]
