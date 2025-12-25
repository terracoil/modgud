"""Port definitions for guard system functionality."""

from typing import Any, Callable, Dict, Optional, Protocol, Tuple, runtime_checkable

# Re-use existing types from the codebase
from ..types import FailureBehavior, GuardFunction


@runtime_checkable
class GuardRuntimePort(Protocol):
  """Port for guard runtime execution and failure handling."""

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
    ...


@runtime_checkable
class GuardWrapperPort(Protocol):
  """Port for wrapping functions with guard checking."""

  def wrap_function(
    self,
    func: Callable,
    guards: Tuple[GuardFunction, ...],
    on_error: FailureBehavior,
    log: bool,
  ) -> Callable:
    """
    Wrap a function with guard checking.

    :param func: Function to wrap
    :param guards: Guards to apply
    :param on_error: Failure behavior
    :param log: Whether to enable logging
    :return: Wrapped function
    """
    ...


@runtime_checkable
class GuardValidatorPort(Protocol):
  """Port for guard validation logic."""

  def validate_guard(self, guard: Any) -> bool:
    """
    Validate that a guard is properly formed.

    :param guard: Guard to validate
    :return: True if valid, False otherwise
    """
    ...

  def create_guard(self, predicate: Callable[..., bool], error_message: str) -> GuardFunction:
    """
    Create a guard function from a predicate and error message.

    :param predicate: Boolean predicate function
    :param error_message: Error message if predicate fails
    :return: Guard function
    """
    ...
