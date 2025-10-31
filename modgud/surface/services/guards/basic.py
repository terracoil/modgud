"""
Basic validation guards for common scenarios.

Provides fundamental validation patterns like not_none, not_empty, and type_check
that form the foundation of most validation requirements.
"""

from typing import Any, Optional, Type, Union

from ....infrastructure import ErrorMessagesModel, GuardFunction
from .base import extract_param


def not_none(param_name: str = 'parameter', position: int = 0) -> GuardFunction:
  """
  Validates that a parameter is not None.

  Args:
      param_name: Name of the parameter to validate
      position: Position of parameter in function args (default: 0)

  Returns:
      Guard function that returns True if parameter is not None

  Example:
      @guarded_expression(not_none('user_id'))
      def process_user(user_id):
          return f"Processing {user_id}"
  """

  def check(*args: Any, **kwargs: Any) -> Union[bool, str]:
    value = extract_param(param_name, position, args, kwargs)
    if value is not None:
      return True
    return ErrorMessagesModel.VALUE_NOT_NONE.format(param_name=param_name)

  return check


def not_empty(param_name: str = 'parameter', position: int = 0) -> GuardFunction:
  """
  Validates that a parameter is not empty (empty string, list, dict, etc.).

  Args:
      param_name: Name of the parameter to validate
      position: Position of parameter in function args

  Returns:
      Guard function that returns True if parameter is not empty
  """

  def check(*args: Any, **kwargs: Any) -> Union[bool, str]:
    value = extract_param(param_name, position, args, kwargs)
    # Check if value supports len() and is not empty
    try:
      if value and len(value) > 0:  # Handles strings, lists, dicts, etc.
        return True
    except TypeError:
      # Value doesn't support len() (like numbers), treat as non-empty if truthy
      if value:
        return True
    return ErrorMessagesModel.VALUE_NOT_EMPTY.format(param_name=param_name)

  return check


def type_check(
  expected_type: Type[Any], param_name: str = 'parameter', position: int = 0
) -> GuardFunction:
  """
  Validates that a parameter is of expected type.

  Args:
      expected_type: The expected type class
      param_name: Name of the parameter to validate
      position: Position of parameter in function args

  Returns:
      Guard function that returns True if parameter matches expected type
  """

  def check(*args: Any, **kwargs: Any) -> Union[bool, str]:
    value = extract_param(param_name, position, args, kwargs)
    if isinstance(value, expected_type):
      return True
    return ErrorMessagesModel.PARAM_MUST_BE_TYPE.format(
      param_name=param_name, expected_type=expected_type.__name__
    )

  return check