"""Adapter implementing GuardRuntimePort using existing GuardRuntime."""

from typing import Any, Dict, Optional, Tuple

from ...domain.types import FailureBehavior, GuardFunction
from ..guard_runtime import GuardRuntime


class GuardRuntimeAdapter:
  """Adapter that implements GuardRuntimePort using GuardRuntime."""

  def __init__(self) -> None:
    """Initialize the adapter."""
    self._runtime = GuardRuntime

  def check_guards(
    self,
    guards: Tuple[GuardFunction, ...],
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
  ) -> Optional[str]:
    """
    Check all guards and return error message if any fail.

    :param guards: Tuple of guard functions to check
    :param args: Positional arguments to pass to guards
    :param kwargs: Keyword arguments to pass to guards
    :return: Error message if any guard fails, None if all pass
    """
    return self._runtime.check_guards(guards, args, kwargs)

  def handle_failure(
    self,
    error_msg: str,
    on_error: FailureBehavior,
    func_name: str,
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
    log_enabled: bool,
  ) -> Tuple[Any, Optional[BaseException]]:
    """
    Handle guard failure according to configuration.

    :param error_msg: The error message from the failed guard
    :param on_error: Failure behavior configuration
    :param func_name: Name of the function being guarded
    :param args: Function arguments for context
    :param kwargs: Function keyword arguments for context
    :param log_enabled: Whether to log the failure
    :return: Tuple of (return_value, exception_to_raise)
    """
    return self._runtime.handle_failure(error_msg, on_error, func_name, args, kwargs, log_enabled)
