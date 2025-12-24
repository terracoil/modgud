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
# Domain enums (from enums package) 
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

# Message templates
from .messages import ErrorMessages, InfoMessages

# Domain protocols (ports) - import both new and legacy aliases
from .protocols import (
  # New port classes
  MaybePort,
  PipeablePort,
  ResultPort,
  # Legacy aliases
  MaybeProtocol,
  PipeableProtocol,
  ResultProtocol,
)
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
  # Ports (new)
  'MaybePort',
  'PipeablePort',
  'ResultPort',
  # Protocols (legacy aliases)
  'MaybeProtocol',
  'PipeableProtocol',
  'ResultProtocol',
  # Enums
  'GuardStrategy',
  'FailureStrategy',
  'ServiceLifetime',
  # Messages
  'ErrorMessages',
  'InfoMessages',
]
