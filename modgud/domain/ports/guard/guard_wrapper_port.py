"""Port definition for wrapping functions with guard checking."""

from typing import Callable, Protocol, Tuple, runtime_checkable

from ...types import FailureBehavior, GuardFunction


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
