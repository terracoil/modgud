"""Validation service implementation - provides guard factory helpers."""

from typing import Any, Callable, Union

from ...domain.messages import ErrorMessages
from ...domain.types import GuardFunction
from ..ports import ValidationServicePort


class ValidationService(ValidationServicePort):
  """
  Production validation service implementation.

  This service implements the high-level ValidationServicePort interface
  to provide helper operations for guard factories.
  """

  def get_error_message(self, message_key: str, **kwargs: Any) -> str:
    """
    Get formatted error message from domain messages.

    Args:
        message_key: Key for message template (e.g., 'POSITIVE', 'NOT_NONE')
        **kwargs: Parameters for message formatting

    Returns:
        Formatted error message string

    """
    template: str = getattr(ErrorMessages, message_key)
    result: str = template.format(**kwargs)
    return result

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

    def guard(*args: Any, **kwargs: Any) -> Union[bool, str]:
      if validation_logic(*args, **kwargs):
        return True
      return error_message

    return guard
