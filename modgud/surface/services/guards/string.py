"""
String validation guards for text-based constraints.

Provides validation patterns for string values including length checks
and regex pattern matching for common string validation scenarios.
"""

import re
from typing import Any, Optional, Union

from ....infrastructure import ErrorMessagesModel, GuardFunction
from .base import extract_param


def length(
  min_length: Optional[int] = None,
  max_length: Optional[int] = None,
  param_name: str = 'parameter',
  position: int = 0,
) -> GuardFunction:
  """
  Validates that a string parameter has length within specified bounds.

  Args:
      min_length: Minimum allowed length (None for no minimum)
      max_length: Maximum allowed length (None for no maximum)
      param_name: Name of the parameter to validate
      position: Position of parameter in function args

  Returns:
      Guard function that returns True if string length is valid
  """

  def check(*args: Any, **kwargs: Any) -> Union[bool, str]:
    value = extract_param(param_name, position, args, kwargs)
    
    if not isinstance(value, str):
      return f"Parameter '{param_name}' must be a string"
    
    length_val = len(value)
    
    if min_length is not None and length_val < min_length:
      return f"Parameter '{param_name}' must be at least {min_length} characters long"
    
    if max_length is not None and length_val > max_length:
      return f"Parameter '{param_name}' must be at most {max_length} characters long"
    
    return True

  return check


def matches_pattern(
  pattern: str, param_name: str = 'parameter', position: int = 0
) -> GuardFunction:
  """
  Validates that a string parameter matches the specified regex pattern.

  Args:
      pattern: Regular expression pattern to match
      param_name: Name of the parameter to validate
      position: Position of parameter in function args

  Returns:
      Guard function that returns True if string matches pattern
  """

  def check(*args: Any, **kwargs: Any) -> Union[bool, str]:
    value = extract_param(param_name, position, args, kwargs)
    
    if not isinstance(value, str):
      return f"Parameter '{param_name}' must be a string"
    
    if re.match(pattern, value):
      return True
    
    return ErrorMessagesModel.PARAM_MUST_MATCH_PATTERN.format(
      param_name=param_name, pattern=pattern
    )

  return check