"""FailureStrategy enum for modgud domain layer.

Enumeration for guard failure handling strategies following domain-driven design
principles. The domain layer is passive and contains no business logic
- only enumeration definitions.
"""

from enum import Enum, auto

__all__ = ['FailureStrategy']


class FailureStrategy(Enum):
  """Strategy for handling guard failures."""

  RAISE_EXCEPTION = auto()  # Raise GuardClauseError
  RETURN_VALUE = auto()  # Return configured failure name
  CALL_HANDLER = auto()  # Call configured failure handler
  LOG_AND_CONTINUE = auto()  # Log failure and continue execution
