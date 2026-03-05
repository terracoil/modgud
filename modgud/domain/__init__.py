"""Domain layer for modgud - passive domain objects.

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
# Domain enums (from enums package)
from .enums import FailureStrategy, GuardStrategy, InfoMessageEnum, ServiceLifetime

# Message templates
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

# Domain protocols (ports)
from .error_messages import ErrorMessages
from .protocols import MaybePort, PipeablePort, ResultPort
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
  'DependencyInjectionError',
  'ServiceNotFoundError',
  # Ports
  'MaybePort',
  'PipeablePort',
  'ResultPort',
  # Enums
  'GuardStrategy',
  'FailureStrategy',
  'ServiceLifetime',
  # Messages
  'ErrorMessages',
  'InfoMessageEnum',
]
