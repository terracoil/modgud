"""
Domain layer - Core models and ports.

Models contain errors, types, messages.
Ports define contracts for infrastructure implementations.
"""

# Models
from .models.error_messages_model import ErrorMessagesModel
from .models.errors import (
  ExplicitReturnDisallowedError,
  GuardClauseError,
  ImplicitReturnError,
  MissingImplicitReturnError,
  UnsupportedConstructError,
)
from .models.info_messages_model import InfoMessagesModel
from .models.types import FailureBehavior, GuardFunction

# Ports
from .ports.ast_transformer_port import AstTransformerPort
from .ports.guard_checker_port import GuardCheckerPort
from .ports.guard_port import GuardPort
from .ports.transform_port import TransformPort
from .ports.validation_port import ValidationPort

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
  'ErrorMessagesModel',
  'InfoMessagesModel',
  # Ports
  'AstTransformerPort',
  'GuardCheckerPort',
  'GuardPort',
  'TransformPort',
  'ValidationPort',
]
