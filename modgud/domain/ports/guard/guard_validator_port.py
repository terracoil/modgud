"""Port definition for guard validation logic."""

from typing import Any, Callable, Protocol, runtime_checkable

from ...types import GuardFunction


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
