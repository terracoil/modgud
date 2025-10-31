"""
Infrastructure layer - Gateway for surface layer.

This module serves as the single import point for the surface layer,
enforcing strict layer isolation. Surface layer ONLY imports from here,
never directly from domain layer.

Following LPA principles:
- Infrastructure (inner layer) defines ports for Surface
- Infrastructure exports domain types/errors for Surface convenience
- Surface (outer layer) depends only on infrastructure contracts
"""

# ruff: noqa: E402

# ==============================================================================
# INFRASTRUCTURE PORTS (for Surface to use)
# ==============================================================================
# ==============================================================================
# INFRASTRUCTURE SERVICES (default implementations of ports)
# ==============================================================================
from modgud.infrastructure.services.guard_service import GuardService
from modgud.infrastructure.services.transform_service import TransformService
from modgud.infrastructure.services.validation_service import ValidationService

# ==============================================================================
# BACKWARD COMPATIBILITY ALIASES (for adapter names)
# ==============================================================================
GuardAdapter = GuardService  # Alias for backward compatibility
TransformAdapter = TransformService  # Alias for backward compatibility
ValidationAdapter = ValidationService  # Alias for backward compatibility

from ..domain.models.error_messages_model import ErrorMessagesModel
from ..domain.models.errors import (
  ExplicitReturnDisallowedError,
  GuardClauseError,
  ImplicitReturnError,
  MissingImplicitReturnError,
  UnsupportedConstructError,
)
from ..domain.models.info_messages_model import InfoMessagesModel

# ==============================================================================
# DOMAIN TYPES (re-exported for Surface convenience)
# ==============================================================================
from ..domain.models.types import FailureBehavior, GuardFunction

# ==============================================================================
# DOMAIN PORTS (re-exported from domain for Surface convenience)
# ==============================================================================
from ..domain.ports.guard_port import GuardPort
from ..domain.ports.transform_port import TransformPort
from ..domain.ports.validation_port import ValidationPort

# ==============================================================================
# PUBLIC API
# ==============================================================================
__all__ = [
  # Infrastructure ports (Surface uses these)
  'GuardPort',
  'TransformPort',
  'ValidationPort',
  # Infrastructure services (default implementations)
  'GuardService',
  'TransformService',
  'ValidationService',
  # Backward compatibility aliases
  'GuardAdapter',
  'TransformAdapter',
  'ValidationAdapter',
  # Domain types (re-exported)
  'GuardFunction',
  'FailureBehavior',
  # Domain errors (re-exported)
  'GuardClauseError',
  'ImplicitReturnError',
  'ExplicitReturnDisallowedError',
  'MissingImplicitReturnError',
  'UnsupportedConstructError',
  # Domain messages (re-exported)
  'ErrorMessagesModel',
  'InfoMessagesModel',
]
