"""
Numeric validation guards for number-based constraints.

Provides validation patterns for numeric values including positive, negative,
and range validation that work with int, float, and other numeric types.
"""

from typing import Any, Optional, Union

from ....infrastructure import ErrorMessagesModel, GuardFunction
from .base import extract_param


def positive(param_name: str = 'parameter', position: int = 0) -> GuardFunction:
  """
  Validates that a numeric parameter is positive (> 0).

  Args:
      param_name: Name of the parameter to validate
      position: Position of parameter in function args

  Returns:
      Guard function that returns True if parameter is positive

  Example:
      @guarded_expression(positive('amount'))
      def calculate_interest(amount):
          return amount * 0.05
  """

  def check(*args: Any, **kwargs: Any) -> Union[bool, str]:
    value = extract_param(param_name, position, args, kwargs)
    if isinstance(value, (int, float)) and value > 0:
      return True
    return ErrorMessagesModel.PARAM_MUST_BE_POSITIVE.format(param_name=param_name)

  return check


def negative(param_name: str = 'parameter', position: int = 0) -> GuardFunction:
  """
  Validates that a numeric parameter is negative (< 0).

  Args:
      param_name: Name of the parameter to validate
      position: Position of parameter in function args

  Returns:
      Guard function that returns True if parameter is negative
  """

  def check(*args: Any, **kwargs: Any) -> Union[bool, str]:
    value = extract_param(param_name, position, args, kwargs)
    if isinstance(value, (int, float)) and value < 0:
      return True
    return f"{param_name} must be negative"

  return check


def in_range(
  min_val: Union[int, float],
  max_val: Union[int, float],
  param_name: str = 'parameter',
  position: int = 0,
) -> GuardFunction:
  """
  Validates that a numeric parameter is within specified range [min_val, max_val].

  Args:
      min_val: Minimum allowed value (inclusive)
      max_val: Maximum allowed value (inclusive)
      param_name: Name of the parameter to validate
      position: Position of parameter in function args

  Returns:
      Guard function that returns True if parameter is in range
  """

  def check(*args: Any, **kwargs: Any) -> Union[bool, str]:
    value = extract_param(param_name, position, args, kwargs)
    if isinstance(value, (int, float)) and min_val <= value <= max_val:
      return True
    return ErrorMessagesModel.PARAM_MUST_BE_IN_RANGE.format(
      param_name=param_name, min_val=min_val, max_val=max_val
    )

  return check