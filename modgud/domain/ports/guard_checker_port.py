"""Guard checker port - contract for guard validation implementations."""

from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple

from ..models.types import FailureBehavior, GuardFunction


class GuardCheckerPort(ABC):
  """
  Port for guard validation logic.

  This port defines the contract that infrastructure adapters must implement
  to provide guard checking and failure handling capabilities.
  """

  @abstractmethod
  def check_guards(
    self, guards: Tuple[GuardFunction, ...], args: Tuple[Any, ...], kwargs: dict[str, Any]
  ) -> Optional[str]:
    """
    Evaluate guards and return error message if any fail.

    Args:
        guards: Tuple of guard functions to evaluate
        args: Positional arguments passed to decorated function
        kwargs: Keyword arguments passed to decorated function

    Returns:
        None if all guards pass, error message string if any guard fails

    """
    pass

  @abstractmethod
  def handle_failure(
    self,
    error_msg: str,
    on_error: FailureBehavior,
    func_name: str,
    args: Tuple[Any, ...],
    kwargs: dict[str, Any],
    log_enabled: bool,
  ) -> Tuple[Any, Optional[BaseException]]:
    """
    Handle guard failure according to on_error strategy.

    Args:
        error_msg: Error message from failed guard
        on_error: Failure behavior (exception class, value, or callable)
        func_name: Name of the decorated function
        args: Positional arguments passed to decorated function
        kwargs: Keyword arguments passed to decorated function
        log_enabled: Whether to log the failure

    Returns:
        Tuple of (return_value, exception) - one will be None

    """
    pass
