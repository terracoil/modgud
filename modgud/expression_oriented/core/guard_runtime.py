"""
Guard checking logic for runtime validation.

Provides the GuardRuntime class that encapsulates guard evaluation and
failure handling logic.
"""

import logging
from typing import Any, Optional, Tuple

from ...domain.types import FailureBehavior, GuardFunction


class GuardRuntime:
  """Runtime guard checking and failure handling."""

  _logger: logging.Logger = logging.getLogger(__name__)

  @classmethod
  def check_guards(
    cls, guards: Tuple[GuardFunction, ...], args: Tuple[Any, ...], kwargs: dict[str, Any]
  ) -> Optional[str]:
    """
    Evaluate all guards sequentially.

    Args:
        guards: Tuple of guard functions to evaluate
        args: Positional arguments passed to the decorated function
        kwargs: Keyword arguments passed to the decorated function

    Returns:
        None if all guards pass, or error message string if any guard fails

    """
    for guard in guards:
      guard_result = guard(*args, **kwargs)
      # Early exit on first failure - fail fast principle
      if guard_result is not True:  # Must be exact True, not just truthy
        return guard_result if isinstance(guard_result, str) else 'Guard clause failed'
    return None

  @classmethod
  def handle_failure(
    cls,
    error_msg: str,
    on_error: FailureBehavior,
    func_name: str,
    args: Tuple[Any, ...],
    kwargs: dict[str, Any],
    log_enabled: bool,
  ) -> Tuple[Any, Optional[BaseException]]:
    """
    Handle guard failure based on on_error configuration.

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
    # Log before handling - capture failure regardless of handler outcome
    if log_enabled:
      cls._logger.info(f'Guard clause failed in {func_name}: {error_msg}')

    # Exception classes raise, callables transform, values pass through
    if isinstance(on_error, type) and issubclass(on_error, BaseException):
      return (None, on_error(error_msg))
    # Callables get full context for recovery logic, values are simple fallbacks
    return (on_error(error_msg, *args, **kwargs) if callable(on_error) else on_error, None)  # type: ignore[call-arg]
