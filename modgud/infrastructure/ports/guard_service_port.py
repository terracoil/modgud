"""Guard service port - high-level contract for guard validation operations."""

from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple

from ...domain.types import FailureBehavior, GuardFunction


class GuardServicePort(ABC):
  """
  High-level guard validation service for Application layer.

  This port defines the contract for guard validation operations that
  the application layer uses. Infrastructure services implement this port.
  """

  @abstractmethod
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

    This is a high-level operation that combines guard checking and
    failure handling in a single call for application convenience.

    Args:
        guards: Tuple of guard functions to evaluate
        args: Positional arguments to validate
        kwargs: Keyword arguments to validate
        on_error: Failure behavior strategy
        log_enabled: Whether to log failures

    Returns:
        Tuple of (success, result, exception):
        - success: True if all guards passed, False otherwise
        - result: Return value if guard failed (None if success or exception)
        - exception: Exception to raise if guard failed (None if success or return value)

    """
    pass
