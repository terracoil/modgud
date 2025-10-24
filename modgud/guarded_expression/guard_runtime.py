"""Pure guard checking logic extracted from guard_clause.

Provides composable functions for evaluating guards and handling failures
without decorator-specific concerns.
"""

import logging
from typing import Any, Optional, Tuple

from ..shared.types import FailureBehavior, GuardFunction

# Module-level logger for guard failures
_logger = logging.getLogger(__name__)


def check_guards(
  guards: Tuple[GuardFunction, ...], args: Tuple[Any, ...], kwargs: dict
) -> Optional[str]:
  """Pure function that evaluates all guards sequentially.

  Args:
      guards: Tuple of guard functions to evaluate
      args: Positional arguments passed to the decorated function
      kwargs: Keyword arguments passed to the decorated function

  Returns:
      None if all guards pass, or error message string if any guard fails

  """
  for guard in guards:
    guard_result = guard(*args, **kwargs)
    # Handle guard failure
    if guard_result is not True:
      return guard_result if isinstance(guard_result, str) else 'Guard clause failed'
  return None


def handle_failure(
  error_msg: str,
  on_error: FailureBehavior,
  func_name: str,
  args: Tuple[Any, ...],
  kwargs: dict,
  log_enabled: bool,
) -> Tuple[Any, Optional[BaseException]]:
  """Pure function that handles guard failure based on on_error configuration.

  Args:
      error_msg: The error message from the failed guard
      on_error: The failure behavior configuration
      func_name: Name of the decorated function (for logging)
      args: Positional arguments passed to the decorated function
      kwargs: Keyword arguments passed to the decorated function
      log_enabled: Whether to log the failure

  Returns:
      Tuple of (return_value, exception_to_raise)
      - If exception should be raised: (None, exception_instance)
      - If value should be returned: (value, None)

  """
  # Log if enabled
  if log_enabled:
    _logger.info(f'Guard clause failed in {func_name}: {error_msg}')

  # Handle failure based on on_error type
  if isinstance(on_error, type) and issubclass(on_error, BaseException):
    return None, on_error(error_msg)

  if callable(on_error):
    return on_error(error_msg, *args, **kwargs), None  # type: ignore[call-arg]

  return on_error, None
