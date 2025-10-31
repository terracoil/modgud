"""
Guard service implementation - validates inputs and handles failures.

Consolidates GuardAdapter and GuardCheckerAdapter into a single service,
eliminating redundant delegation layers while maintaining port contracts.
"""

import logging
from typing import Any, Optional, Tuple

from ...domain.models.types import FailureBehavior, GuardFunction
from ...domain.ports.guard_checker_port import GuardCheckerPort
from ...domain.ports.guard_port import GuardPort


class GuardService(GuardPort, GuardCheckerPort):
  """
  Consolidated guard service implementing both high-level and low-level ports.

  This service directly implements guard validation and failure handling,
  eliminating the redundant adapter delegation pattern while maintaining
  backward compatibility with both port interfaces.
  """

  _logger: logging.Logger = logging.getLogger(__name__)

  def validate_inputs(
    self,
    guards: Tuple[GuardFunction, ...],
    args: Tuple[Any, ...],
    kwargs: dict[str, Any],
    on_error: FailureBehavior,
    log_enabled: bool,
  ) -> Tuple[bool, Optional[Any], Optional[BaseException]]:
    """
    Validate inputs against guards and handle failures.

    Args:
        guards: Tuple of guard functions to evaluate
        args: Positional arguments to validate
        kwargs: Keyword arguments to validate
        on_error: Failure behavior strategy
        log_enabled: Whether to log failures

    Returns:
        Tuple of (success, result, exception)

    """
    error_msg = self.check_guards(guards, args, kwargs)

    if error_msg is None:
      return (True, None, None)

    result, exception = self.handle_failure(error_msg, on_error, '', args, kwargs, log_enabled)
    return (False, result, exception)

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
