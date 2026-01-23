"""Service implementing GuardWrapperPort for wrapping functions with guards."""

import functools
from typing import Any, Callable, Tuple

from modgud.domain import FailureBehavior, GuardFunction
from modgud.domain.ports import GuardRuntimePort


class GuardWrapperService:
  """Service that wraps functions with guard checking."""

  def __init__(self, runtime: GuardRuntimePort) -> None:
    """Initialize with a guard runtime.

    :param runtime: Guard runtime implementation
    """
    self._runtime = runtime

  def wrap_function(
    self,
    func: Callable,
    guards: Tuple[GuardFunction, ...],
    on_error: FailureBehavior,
    log: bool,
  ) -> Callable:
    """Wrap a function with guard checking.

    :param func: Function to wrap
    :param guards: Guards to apply
    :param on_error: Failure behavior
    :param log: Whether to enable logging
    :return: Wrapped function
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
      # Check guards first
      error_msg = self._runtime.check_guards(guards, args, kwargs)

      if error_msg is None:
        # All guards passed - execute the function
        return func(*args, **kwargs)

      # Handle guard failure
      return_value, exception = self._runtime.handle_failure(
        error_msg, on_error, func.__name__, args, kwargs, log
      )

      if exception:
        raise exception
      return return_value

    # Preserve metadata
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__dict__.update(func.__dict__)

    return wrapper
