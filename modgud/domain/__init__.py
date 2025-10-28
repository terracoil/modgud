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
]
