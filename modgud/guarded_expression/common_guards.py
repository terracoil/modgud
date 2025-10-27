"""Common guard validators for typical validation scenarios.

Provides pre-built guard functions through the CommonGuards class for
common validation patterns like not_none, positive, in_range, etc.
"""

import re
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional, Union
from urllib.parse import urlparse

from .messages import ErrorMessages
from .types import GuardFunction


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
    param_name: str,
    position: Optional[int],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    default: Any = None,
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
    result = default
    if param_name in kwargs:
      result = kwargs[param_name]
    else:
      # Use explicit position if provided, else default to first arg
      pos = position if position is not None else 0
      if 0 <= pos < len(args):
        result = args[pos]
    return result

  @staticmethod
  def _make_guard(
    param_name: str,
    position: Optional[int],
    validator: Callable[[Any], bool],
    error_template: str,
    default: Any = None,
  ) -> GuardFunction:
    """Create common guard patterns with a factory method.

    Args:
        param_name: Name of the parameter to check
        position: Position for positional args
        validator: Function that validates the value, returns bool
        error_template: Error message template with {param_name} and {value} placeholders
        default: Default value if parameter not found

    Returns:
        GuardFunction that validates parameters

    """

    def check(*args: Any, **kwargs: Any) -> Union[bool, str]:
      value = CommonGuards._extract_param(param_name, position, args, kwargs, default)
      # Single return point
      result: Union[bool, str] = True
      if not validator(value):
        result = error_template.format(param_name=param_name, value=value)
      return result

    return check

  @staticmethod
  def not_empty(param_name: str = 'parameter', position: Optional[int] = None) -> GuardFunction:
    """Guard ensuring collection parameter is not empty.

    Args:
        param_name: Name of the parameter to check
        position: Optional explicit position for positional args (0-based)

    """

    def check(*args: Any, **kwargs: Any) -> Union[bool, str]:
      # Single return point - delegate to static method
      return CommonGuards._check_not_empty(param_name, position, args, kwargs)

    return check

  @staticmethod
  def not_none(param_name: str = 'parameter', position: int = 0) -> GuardFunction:
    """Guard ensuring parameter is not None.

    Args:
        param_name: Name of the parameter to check
        position: Position for positional args (default: 0)

    """
    return CommonGuards._make_guard(
      param_name, position, lambda v: v is not None, '{param_name} cannot be None', default=None
    )

  @staticmethod
  def positive(param_name: str = 'parameter', position: int = 0) -> GuardFunction:
    """Guard ensuring parameter is positive.

    Args:
        param_name: Name of the parameter to check
        position: Position for positional args (default: 0)

    """
    return CommonGuards._make_guard(
      param_name, position, lambda v: v > 0, ErrorMessages.PARAM_MUST_BE_POSITIVE, default=0
    )

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

    def check(*args: Any, **kwargs: Any) -> Union[bool, str]:
      # Single return point - delegate to static method
      return CommonGuards._check_in_range(min_val, max_val, param_name, position, args, kwargs)

    return check

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

    def check(*args: Any, **kwargs: Any) -> Union[bool, str]:
      # Single return point - delegate to static method
      return CommonGuards._check_type(expected_type, param_name, position, args, kwargs)

    return check

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

    def check(*args: Any, **kwargs: Any) -> Union[bool, str]:
      # Single return point - delegate to static method
      return CommonGuards._check_pattern(pattern, param_name, position, args, kwargs)

    return check

  @staticmethod
  def valid_file_path(
    param_name: str = 'path',
    position: int = 0,
    must_exist: bool = True,
    must_be_file: bool = False,
    must_be_dir: bool = False,
  ) -> GuardFunction:
    """Guard ensuring parameter is a valid file path.

    Args:
        param_name: Name of the parameter to check
        position: Position for positional args (default: 0)
        must_exist: If True, path must exist (default: True)
        must_be_file: If True, path must be a file (default: False)
        must_be_dir: If True, path must be a directory (default: False)

    """

    def check(*args: Any, **kwargs: Any) -> Union[bool, str]:
      # Single return point - delegate to static method
      return CommonGuards._check_file_path(
        param_name, position, must_exist, must_be_file, must_be_dir, args, kwargs
      )

    return check

  @staticmethod
  def valid_url(
    param_name: str = 'url', position: int = 0, require_scheme: bool = True
  ) -> GuardFunction:
    """Guard ensuring parameter is a valid URL.

    Args:
        param_name: Name of the parameter to check
        position: Position for positional args (default: 0)
        require_scheme: If True, URL must have scheme (http/https) (default: True)

    """

    def check(*args: Any, **kwargs: Any) -> Union[bool, str]:
      # Single return point - delegate to static method
      return CommonGuards._check_url(param_name, position, require_scheme, args, kwargs)

    return check

  @staticmethod
  def valid_enum(
    enum_class: type[Enum], param_name: str = 'parameter', position: int = 0
  ) -> GuardFunction:
    """Guard ensuring parameter is a valid enum value.

    Args:
        enum_class: The Enum class to validate against
        param_name: Name of the parameter to check
        position: Position for positional args (default: 0)

    """

    def check(*args: Any, **kwargs: Any) -> Union[bool, str]:
      # Single return point - delegate to static method
      return CommonGuards._check_enum(enum_class, param_name, position, args, kwargs)

    return check

  # ============= Private Static Check Methods =============
  # These methods implement the actual validation logic with single return point

  @staticmethod
  def _check_not_empty(
    param_name: str,
    position: Optional[int],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
  ) -> Union[bool, str]:
    """Check if parameter is not empty (single return point)."""
    value = CommonGuards._extract_param(param_name, position, args, kwargs, default='')
    result: Union[bool, str] = True

    # Check if value is empty (works for strings and collections)
    if hasattr(value, '__len__'):
      if len(value) == 0:
        result = f'{param_name} cannot be empty'
    elif not bool(value):
      result = f'{param_name} cannot be empty'

    return result

  @staticmethod
  def _check_in_range(
    min_val: float,
    max_val: float,
    param_name: str,
    position: int,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
  ) -> Union[bool, str]:
    """Check if parameter is within range (single return point)."""
    value = CommonGuards._extract_param(param_name, position, args, kwargs, default=min_val - 1)
    result: Union[bool, str] = True

    if not (min_val <= value <= max_val):
      result = f'{param_name} must be between {min_val} and {max_val}'

    return result

  @staticmethod
  def _check_type(
    expected_type: type,
    param_name: str,
    position: int,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
  ) -> Union[bool, str]:
    """Check if parameter matches expected type (single return point)."""
    value = CommonGuards._extract_param(param_name, position, args, kwargs, default=None)
    result: Union[bool, str] = True

    if not isinstance(value, expected_type):
      result = f'{param_name} must be of type {expected_type.__name__}'

    return result

  @staticmethod
  def _check_pattern(
    pattern: str,
    param_name: str,
    position: int,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
  ) -> Union[bool, str]:
    """Check if parameter matches regex pattern (single return point)."""
    value = str(CommonGuards._extract_param(param_name, position, args, kwargs, default=''))
    result: Union[bool, str] = True

    if re.match(pattern, value) is None:
      result = f'{param_name} must match pattern {pattern}'

    return result

  @staticmethod
  def _check_file_path(
    param_name: str,
    position: int,
    must_exist: bool,
    must_be_file: bool,
    must_be_dir: bool,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
  ) -> Union[bool, str]:
    """Check if parameter is a valid file path (single return point)."""
    value = CommonGuards._extract_param(param_name, position, args, kwargs, default=None)
    result: Union[bool, str] = True

    if value is None:
      result = f'{param_name} is required'
    else:
      path = Path(value)
      if must_exist and not path.exists():
        result = f'{param_name} does not exist: {value}'
      elif must_be_file and not path.is_file():
        result = f'{param_name} must be a file: {value}'
      elif must_be_dir and not path.is_dir():
        result = f'{param_name} must be a directory: {value}'

    return result

  @staticmethod
  def _check_url(
    param_name: str,
    position: int,
    require_scheme: bool,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
  ) -> Union[bool, str]:
    """Check if parameter is a valid URL (single return point)."""
    value = CommonGuards._extract_param(param_name, position, args, kwargs, default=None)
    result: Union[bool, str] = True

    if value is None:
      result = f'{param_name} is required'
    else:
      parsed = urlparse(str(value))
      if require_scheme and not parsed.scheme:
        result = f'{param_name} must include a scheme (http/https): {value}'
      elif not parsed.netloc and not parsed.path:
        result = f'{param_name} is not a valid URL: {value}'

    return result

  @staticmethod
  def _check_enum(
    enum_class: type[Enum],
    param_name: str,
    position: int,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
  ) -> Union[bool, str]:
    """Check if parameter is a valid enum value (single return point)."""
    value = CommonGuards._extract_param(param_name, position, args, kwargs, default=None)
    result: Union[bool, str] = True

    if value is None:
      result = f'{param_name} is required'
    elif isinstance(value, enum_class):
      # Value is already an enum instance
      pass  # result stays True
    elif isinstance(value, str):
      # Try to convert string to enum
      try:
        enum_class(value)
      except ValueError:
        valid_values = [e.value for e in enum_class]
        result = f'{param_name} must be one of {valid_values}: got {value}'
    else:
      result = f'{param_name} must be a valid {enum_class.__name__} value'

    return result


def _register_common_guards() -> None:
  """Auto-register all CommonGuards methods to global registry."""
  from .guard_registry import register_guard

  # List of guard methods to register (excluding private methods)
  guards_to_register = [
    'not_empty',
    'not_none',
    'positive',
    'in_range',
    'type_check',
    'matches_pattern',
    'valid_file_path',
    'valid_url',
    'valid_enum',
  ]

  for name in guards_to_register:
    method = getattr(CommonGuards, name, None)
    if callable(method):
      register_guard(name, method, namespace='common')


# Auto-register CommonGuards on module import
_register_common_guards()
