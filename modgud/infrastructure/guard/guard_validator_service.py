"""Service for guard validation."""

from typing import Any, Callable

from modgud.domain import GuardFunction


class GuardValidatorService:
  """Service for validating and creating guards."""

  def validate_guard(self, guard: Any) -> bool:
    """Validate that a guard is properly formed.

    :param guard: Guard to validate
    :return: True if valid, False otherwise
    """
    # A valid guard must be callable
    if not callable(guard):
      return False

    # Check if it has the right signature (accepts *args, **kwargs)
    try:
      # Try to call with dummy args - a proper guard should handle any args
      result = guard(None)
      # Result should be either True or a string error message
      return isinstance(result, (bool, str))
    except Exception:
      # If it throws on dummy args, it's not a valid guard
      return False

  def create_guard(self, predicate: Callable[..., bool], error_message: str) -> GuardFunction:
    """Create a guard function from a predicate and error message.

    :param predicate: Boolean predicate function
    :param error_message: Error message if predicate fails
    :return: Guard function
    """

    def guard(*args: Any, **kwargs: Any) -> bool | str:
      """Validate arguments against the predicate."""
      try:
        if predicate(*args, **kwargs):
          return True
        return error_message
      except Exception as e:
        # If predicate throws, return error message with exception info
        return f'{error_message}: {str(e)}'

    # Set helpful name for debugging
    guard.__name__ = f'guard_{predicate.__name__}'
    guard.__doc__ = f'Guard: {error_message}'

    return guard
