"""
Domain layer for modgud - passive domain objects.

This package contains the core domain concepts for modgud including:
- Types and type definitions
- Domain exceptions
- Domain protocols (interfaces)
- Domain enums and constants
- Message templates

The domain layer is completely passive - it contains no business logic,
only data structures and interface definitions.
"""

# Core types
# Domain enums
from .enums import FailureStrategy, GuardStrategy, ServiceLifetime

# Domain exceptions
from .exceptions import (
  DependencyInjectionError,
  ExplicitReturnDisallowedError,
  GuardClauseError,
  ImplicitReturnError,
  MissingImplicitReturnError,
  ServiceNotFoundError,
  UnsupportedConstructError,
)

# Domain protocols
from .maybe_protocol import MaybeProtocol

# Message templates
from .messages import ErrorMessages, InfoMessages
from .result_protocol import ResultProtocol
from .types import FailureBehavior, FailureTypes, GuardFunction

__all__ = [
  # Types
  'GuardFunction',
  'FailureTypes',
  'FailureBehavior',
  # Exceptions
  'GuardClauseError',
  'ImplicitReturnError',
  'ExplicitReturnDisallowedError',
  'MissingImplicitReturnError',
  'UnsupportedConstructError',
  'DependencyInjectionError',
  'ServiceNotFoundError',
  # Protocols
  'MaybeProtocol',
  'ResultProtocol',
  # Enums
  'GuardStrategy',
  'FailureStrategy',
  'ServiceLifetime',
  # Messages
  'ErrorMessages',
  'InfoMessages',
]
