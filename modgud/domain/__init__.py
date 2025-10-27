"""Domain layer - Core types, errors, and contracts."""

from .errors import (
  ExplicitReturnDisallowedError,
  GuardClauseError,
  ImplicitReturnError,
  MissingImplicitReturnError,
  UnsupportedConstructError,
)
from .ports import AstTransformerPort, GuardCheckerPort
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
  # Ports
  'GuardCheckerPort',
  'AstTransformerPort',
]
