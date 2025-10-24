"""Common guard validators for typical validation scenarios.

Provides pre-built guard functions through the CommonGuards class for
common validation patterns like not_none, positive, in_range, etc.
"""

import re
from typing import Any, Optional, Union

from ..shared.types import GuardFunction


class CommonGuards:

  """Pre-defined common guard clauses.

  Usage:
      @guarded_expression(
          CommonGuards.not_empty("username"),
          log=True
      )
      def create_user(username):
          return {"username": username}
  """

  @staticmethod
  def _extract_param(
    param_name: str, position: Optional[int], args: tuple, kwargs: dict, default: Any = None
  ) -> Any:
    """Extract parameter value from args or kwargs.

    Args:
        param_name: Name of the parameter in kwargs
        position: Position in args (None means first arg)
        args: Positional arguments tuple
        kwargs: Keyword arguments dict
        default: Default value if not found

    Returns:
        Parameter value or default

    """
    if param_name in kwargs:
      return kwargs[param_name]

    # Use explicit position if provided, else default to first arg
    pos = position if position is not None else 0
    if 0 <= pos < len(args):
      return args[pos]

    return default

  @staticmethod
  def not_empty(param_name: str = 'parameter', position: Optional[int] = None) -> GuardFunction:
    """Guard ensuring collection parameter is not empty.

    Args:
        param_name: Name of the parameter to check
        position: Optional explicit position for positional args (0-based)

    """

    def check_not_empty(*args: Any, **kwargs: Any) -> Union[bool, str]:
      value = CommonGuards._extract_param(param_name, position, args, kwargs, default='')

      # Check if value is empty (works for strings and collections)
      if hasattr(value, '__len__'):
        return len(value) > 0 or f'{param_name} cannot be empty'

      return bool(value) or f'{param_name} cannot be empty'

    return check_not_empty

  @staticmethod
  def not_none(param_name: str = 'parameter', position: int = 0) -> GuardFunction:
    """Guard ensuring parameter is not None.

    Args:
        param_name: Name of the parameter to check
        position: Position for positional args (default: 0)

    """

    def check_not_none(*args: Any, **kwargs: Any) -> Union[bool, str]:
      value = CommonGuards._extract_param(param_name, position, args, kwargs, default=None)
      return value is not None or f'{param_name} cannot be None'

    return check_not_none

  @staticmethod
  def positive(param_name: str = 'parameter', position: int = 0) -> GuardFunction:
    """Guard ensuring parameter is positive.

    Args:
        param_name: Name of the parameter to check
        position: Position for positional args (default: 0)

    """

    def check_positive(*args: Any, **kwargs: Any) -> Union[bool, str]:
      value = CommonGuards._extract_param(param_name, position, args, kwargs, default=0)
      return value > 0 or f'{param_name} must be positive'

    return check_positive

  @staticmethod
  def in_range(
    min_val: float, max_val: float, param_name: str = 'parameter', position: int = 0
  ) -> GuardFunction:
    """Guard ensuring parameter is within range [min_val, max_val].

    Args:
        min_val: Minimum value (inclusive)
        max_val: Maximum value (inclusive)
        param_name: Name of the parameter to check
        position: Position for positional args (default: 0)

    """

    def check_in_range(*args: Any, **kwargs: Any) -> Union[bool, str]:
      value = CommonGuards._extract_param(param_name, position, args, kwargs, default=min_val - 1)
      return min_val <= value <= max_val or f'{param_name} must be between {min_val} and {max_val}'

    return check_in_range

  @staticmethod
  def type_check(
    expected_type: type, param_name: str = 'parameter', position: int = 0
  ) -> GuardFunction:
    """Guard ensuring parameter matches expected type.

    Args:
        expected_type: Expected type for the parameter
        param_name: Name of the parameter to check
        position: Position for positional args (default: 0)

    """

    def check_type(*args: Any, **kwargs: Any) -> Union[bool, str]:
      value = CommonGuards._extract_param(param_name, position, args, kwargs, default=None)
      return (
        isinstance(value, expected_type) or f'{param_name} must be of type {expected_type.__name__}'
      )

    return check_type

  @staticmethod
  def matches_pattern(
    pattern: str, param_name: str = 'parameter', position: int = 0
  ) -> GuardFunction:
    """Guard ensuring string parameter matches regex pattern.

    Args:
        pattern: Regular expression pattern to match
        param_name: Name of the parameter to check
        position: Position for positional args (default: 0)

    """

    def check_pattern(*args: Any, **kwargs: Any) -> Union[bool, str]:
      value = str(CommonGuards._extract_param(param_name, position, args, kwargs, default=''))
      return re.match(pattern, value) is not None or f'{param_name} must match pattern {pattern}'

    return check_pattern
