"""
Enum validation guard for checking enum membership.

Provides validation for enum values to ensure parameters match
expected enumeration values or choices from a predefined set.
"""

from enum import Enum
from typing import Any, Optional, Union

from ....infrastructure import ErrorMessagesModel, GuardFunction
from .base import extract_param


def valid_enum(
  enum_class: type[Enum], param_name: str = 'parameter', position: int = 0
) -> GuardFunction:
  """
  Validates that a parameter is a valid member of the specified enum.

  Args:
      enum_class: The enum class to validate against
      param_name: Name of the parameter to validate
      position: Position of parameter in function args

  Returns:
      Guard function that returns True if parameter is valid enum member

  Example:
      from enum import Enum
      
      class Status(Enum):
          ACTIVE = "active"
          INACTIVE = "inactive"
          PENDING = "pending"

      @guarded_expression(valid_enum(Status, 'status'))
      def update_status(status):
          return f"Status updated to {status.value}"
  """

  def check(*args: Any, **kwargs: Any) -> Union[bool, str]:
    value = extract_param(param_name, position, args, kwargs)
    
    # Check for None values first - treat as missing required parameter
    if value is None:
      return f"{param_name} is required"
    
    # Handle both enum instances and raw values
    if isinstance(value, enum_class):
      return True
    
    # Check if the value matches any enum value
    try:
      enum_class(value)
      return True
    except ValueError:
      valid_values = [member.value for member in enum_class]
      return ErrorMessagesModel.ENUM_INVALID_VALUE.format(
        param_name=param_name, value=value, valid_values=valid_values
      )

  return check