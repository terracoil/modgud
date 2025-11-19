"""
Domain enums for modgud.

Enumeration classes for domain concepts following domain-driven design 
principles. The domain layer is passive and contains no business logic
- only enumeration definitions.
"""

from enum import Enum, auto

__all__ = [
  'GuardStrategy',
  'FailureStrategy', 
  'ServiceLifetime',
]


class GuardStrategy(Enum):
  """Strategy for how guards should be evaluated."""
  
  FAIL_FAST = auto()     # Stop on first guard failure
  COLLECT_ALL = auto()   # Evaluate all guards and collect failures
  WARN_ONLY = auto()     # Log warnings but don't fail


class FailureStrategy(Enum):
  """Strategy for handling guard failures."""
  
  RAISE_EXCEPTION = auto()  # Raise GuardClauseError
  RETURN_VALUE = auto()     # Return configured failure value
  CALL_HANDLER = auto()     # Call configured failure handler
  LOG_AND_CONTINUE = auto() # Log failure and continue execution


class ServiceLifetime(Enum):
  """Lifetime strategy for dependency injection services."""
  
  SINGLETON = auto()    # Single instance per container
  TRANSIENT = auto()    # New instance per request
  SCOPED = auto()       # Single instance per scope/request context