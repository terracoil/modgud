"""Domain layer for modgud - passive domain objects.

This package contains the core domain concepts for modgud including:
- Types and type definitions
- Domain exceptions
- The GuardFailureStrategy enum
- Message templates

The domain layer is completely passive - it contains no business logic,
only data structures and interface definitions.
"""

from .enums import GuardFailureStrategy
from .error_messages import ErrorMessages
from .exceptions import (
  ExplicitReturnDisallowedError,
  GuardClauseError,
  ImplicitReturnError,
  MissingImplicitReturnError,
  UnsupportedConstructError,
)
from .types import GuardFunction

__all__ = [
  # Types
  'GuardFunction',
  # Error messages
  'ErrorMessages',
  # Exceptions
  'GuardClauseError',
  'ImplicitReturnError',
  'ExplicitReturnDisallowedError',
  'MissingImplicitReturnError',
  'UnsupportedConstructError',
  # Enums
  'GuardFailureStrategy',
]
