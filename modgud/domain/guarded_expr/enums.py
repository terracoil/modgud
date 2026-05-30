"""Guard failure strategy enum for modgud.

Defines how `@guarded_expression` reacts when one or more guards report
failure. Single-enum design: strategy + on_failure payload + continuance
budget on the decorator cover every combination cleanly.
"""

from enum import IntEnum, auto

__all__ = ['GuardFailureStrategy']


class GuardFailureStrategy(IntEnum):
  """How @guarded_expression reacts when one or more guards report failure."""

  ERROR_RAISE = auto()  # Raise GuardClauseError with all failures (if any occurred)
  ERROR_RETURN = auto()  # Return GuardClauseError with all failures (if any occurred)
  RETURN_VALUE = auto()  # Return configured failure value (e.g., False)
  CALL_HANDLER = auto()  # Call configured failure handler and return its value
