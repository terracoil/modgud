"""
Infrastructure layer - Gateway for application layer.

This module serves as the single import point for the application layer,
enforcing strict layer isolation. Application layer ONLY imports from here,
never directly from domain layer.

Following LPA principles:
- Infrastructure (inner layer) defines ports for Application
- Infrastructure exports domain types/errors for Application convenience
- Application (outer layer) depends only on infrastructure contracts
"""

# ==============================================================================
# INFRASTRUCTURE PORTS (for Application to use)
# ==============================================================================
# ==============================================================================
# DOMAIN ERRORS (re-exported for Application convenience)
# ==============================================================================
from ..domain.errors import (
  ExplicitReturnDisallowedError,
  GuardClauseError,
  ImplicitReturnError,
  MissingImplicitReturnError,
  UnsupportedConstructError,
)

# ==============================================================================
# DOMAIN MESSAGES (re-exported for Application convenience)
# ==============================================================================
from ..domain.messages import ErrorMessages, InfoMessages

# ==============================================================================
# DOMAIN TYPES (re-exported for Application convenience)
# ==============================================================================
from ..domain.types import FailureBehavior, GuardFunction
from .ports import GuardServicePort, TransformServicePort, ValidationServicePort

# ==============================================================================
# INFRASTRUCTURE SERVICES (default implementations of ports)
# ==============================================================================
from .services import GuardService, TransformService, ValidationService

# ==============================================================================
# PUBLIC API
# ==============================================================================
__all__ = [
  # Infrastructure ports (Application uses these)
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
  'ErrorMessages',
  'InfoMessages',
]
