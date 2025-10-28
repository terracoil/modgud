"""Guard service implementation - validates inputs using guard checker adapter."""

from typing import Any, Optional, Tuple

from ...domain.ports import GuardCheckerPort
from ...domain.types import FailureBehavior, GuardFunction
from ..ports import GuardServicePort


class GuardService(GuardServicePort):
  """
  Production guard service implementation.

  This service implements the high-level GuardServicePort interface
  by delegating to a GuardCheckerPort implementation (adapter).
  """

  def __init__(self, checker: Optional[GuardCheckerPort] = None):
    """
    Initialize guard service.

    Args:
        checker: Optional guard checker adapter. If None, default will be lazy-loaded.

    """
    self._checker = checker

  @property
  def checker(self) -> GuardCheckerPort:
    """Lazy-load default guard checker if not injected."""
    if self._checker is None:
      from ..adapters.guard_checker import DefaultGuardChecker

      self._checker = DefaultGuardChecker()
    return self._checker

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

    Delegates to guard checker adapter for low-level operations.

    Args:
        guards: Tuple of guard functions to evaluate
        args: Positional arguments to validate
        kwargs: Keyword arguments to validate
        on_error: Failure behavior strategy
        log_enabled: Whether to log failures

    Returns:
        Tuple of (success, result, exception)

    """
    error_msg = self.checker.check_guards(guards, args, kwargs)

    if error_msg is None:
      return (True, None, None)

    result, exception = self.checker.handle_failure(
      error_msg, on_error, '', args, kwargs, log_enabled
    )
    return (False, result, exception)
