"""Validation service implementation - provides guard factory helpers."""

from typing import Any, Callable, Union

from modgud.domain.models.error_messages_model import ErrorMessagesModel
from modgud.domain.models.types import GuardFunction
from modgud.domain.ports.validation_port import ValidationPort


class ValidationAdapter(ValidationPort):
  """
  Production validation service implementation.

  This service implements the high-level ValidationPort interface
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
    template: str = getattr(ErrorMessagesModel, message_key)
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
