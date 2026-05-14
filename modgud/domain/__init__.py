"""Domain layer for modgud - passive domain objects.

This package contains the core domain concepts for modgud including:
- Types and type definitions
- Domain exceptions
- Domain enums and constants
- Message templates

The domain layer is completely passive - it contains no business logic,
only data structures and interface definitions.
"""

# Core types
# Domain enums (from enums package)
from .enums import FailureStrategy, GuardStrategy, InfoMessageEnum

# Message templates
from .error_messages import ErrorMessages

# Domain exceptions
from .exceptions import (
  ExplicitReturnDisallowedError,
  GuardClauseError,
  ImplicitReturnError,
  MissingImplicitReturnError,
  UnsupportedConstructError,
)
from .types import FailureBehavior, FailureTypes, GuardFunction

__all__ = [
  # Types
  'GuardFunction',
  'FailureTypes',
  'FailureBehavior',
  # Error messages
  'ErrorMessages',
  # Exceptions
  'GuardClauseError',
  'ImplicitReturnError',
  'ExplicitReturnDisallowedError',
  'MissingImplicitReturnError',
  'UnsupportedConstructError',
  # Enums
  'GuardStrategy',
  'FailureStrategy',
  'InfoMessageEnum',
]
