"""Validation service port - high-level contract for guard factory operations."""

from abc import ABC, abstractmethod
from typing import Any, Callable

from ...domain.types import GuardFunction


class ValidationServicePort(ABC):
  """
  High-level validation operations for guard factories.

  This port defines the contract for validation helper operations that
  guard factories (CommonGuards) use. Infrastructure services implement this port.
  """

  @abstractmethod
  def get_error_message(self, message_key: str, **kwargs: Any) -> str:
    """
    Get formatted error message from domain messages.

    Args:
        message_key: Key for message template (e.g., 'POSITIVE', 'NOT_NONE')
        **kwargs: Parameters for message formatting

    Returns:
        Formatted error message string

    """
    pass

  @abstractmethod
  def create_guard_function(
    self,
    validation_logic: Callable[..., bool],
    error_message: str,
  ) -> GuardFunction:
    """
    Create a guard function with proper signature.

    Wraps validation logic in a guard function that returns True on success
    or error_message on failure.

    Args:
        validation_logic: Function that returns True if valid, False otherwise
        error_message: Error message to return on validation failure

    Returns:
        Guard function with signature (*args, **kwargs) -> Union[bool, str]

    """
    pass
