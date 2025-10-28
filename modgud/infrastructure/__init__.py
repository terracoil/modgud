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
# DOMAIN ERRORS (re-exported for Surface convenience)
# ==============================================================================
# ==============================================================================
# DOMAIN MESSAGES (re-exported for Surface convenience)
# ==============================================================================
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
# INFRASTRUCTURE PORTS (for Surface to use)
# ==============================================================================
from .ports.guard_service_port import GuardServicePort
from .ports.transform_service_port import TransformServicePort
from .ports.validation_service_port import ValidationServicePort

# ==============================================================================
# INFRASTRUCTURE SERVICES (default implementations of ports)
# ==============================================================================
from .services.guard_service import GuardService
from .services.transform_service import TransformService
from .services.validation_service import ValidationService

# ==============================================================================
# PUBLIC API
# ==============================================================================
__all__ = [
  # Infrastructure ports (Surface uses these)
  'GuardServicePort',
  'TransformServicePort',
  'ValidationServicePort',
  # Infrastructure services (default implementations)
  'GuardService',
  'TransformService',
  'ValidationService',
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
