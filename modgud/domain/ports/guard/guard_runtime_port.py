"""Port definition for guard runtime execution and failure handling."""

from typing import Any, Dict, Optional, Protocol, Tuple, runtime_checkable

from modgud.domain.types import FailureBehavior, GuardFunction


@runtime_checkable
class GuardRuntimePort(Protocol):
  """Port for guard runtime execution and failure handling."""

  def check_guards(
    self,
    guards: Tuple[GuardFunction, ...],
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
  ) -> Optional[str]:
    """Check all guards and return error message if any fail.

    :param guards: Tuple of guard functions to check
    :param args: Positional arguments to pass to guards
    :param kwargs: Keyword arguments to pass to guards
    :return: Error message if any guard fails, None if all pass
    """
    ...

  def handle_failure(
    self,
    error_msg: str,
    on_error: FailureBehavior,
    func_name: str,
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
    log_enabled: bool,
  ) -> Tuple[Any, Optional[BaseException]]:
    """Handle guard failure according to configuration.

    :param error_msg: The error message from the failed guard
    :param on_error: Failure behavior configuration
    :param func_name: Name of the function being guarded
    :param args: Function arguments for context
    :param kwargs: Function keyword arguments for context
    :param log_enabled: Whether to log the failure
    :return: Tuple of (return_value, exception_to_raise)
    """
    ...
