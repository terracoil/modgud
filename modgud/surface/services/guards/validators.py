"""
Specialized validators for common data formats.

Provides validation patterns for common data formats like emails, URLs, UUIDs,
and file paths that require more complex validation logic.
"""

import re
from pathlib import Path
from typing import Any, Optional, Union
from urllib.parse import urlparse

from ....infrastructure import ErrorMessagesModel, GuardFunction
from .base import extract_param

# Pre-compiled regex patterns for performance
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)


def valid_email(param_name: str = 'parameter', position: int = 0) -> GuardFunction:
  """
  Validates that a parameter is a valid email address format.

  Args:
      param_name: Name of the parameter to validate
      position: Position of parameter in function args

  Returns:
      Guard function that returns True if parameter is valid email format
  """

  def check(*args: Any, **kwargs: Any) -> Union[bool, str]:
    value = extract_param(param_name, position, args, kwargs)
    
    if not isinstance(value, str):
      return f"Parameter '{param_name}' must be a string"
    
    if EMAIL_PATTERN.match(value):
      return True
    
    return f"{param_name} must be a valid email address: {value}"

  return check


def valid_url(param_name: str = 'parameter', position: int = 0, require_scheme: bool = True) -> GuardFunction:
  """
  Validates that a parameter is a valid URL format.

  Args:
      param_name: Name of the parameter to validate
      position: Position of parameter in function args
      require_scheme: Whether URL must have a scheme (http/https)

  Returns:
      Guard function that returns True if parameter is valid URL format
  """

  def check(*args: Any, **kwargs: Any) -> Union[bool, str]:
    value = extract_param(param_name, position, args, kwargs)
    
    if not isinstance(value, str):
      return f"Parameter '{param_name}' must be a string"
    
    parsed = urlparse(value)
    
    if require_scheme and not parsed.scheme:
      return ErrorMessagesModel.URL_MUST_HAVE_SCHEME.format(param_name=param_name, value=value)
    
    # Valid URL with scheme and netloc
    if parsed.scheme and parsed.netloc:
      return True
    
    # Handle case where no scheme is provided but require_scheme=False
    if not require_scheme and not parsed.scheme and not parsed.netloc:
      # urlparse puts everything in path when no scheme, check if path looks like domain
      # Basic check: should contain at least one dot or slash (domain.com or localhost/path)
      path_part = parsed.path.strip()
      if path_part and ('.' in path_part or '/' in path_part):
        return True
    
    # Valid URL without scheme but with netloc (shouldn't happen with urlparse, but just in case)
    if not require_scheme and parsed.netloc:
      return True
    
    return ErrorMessagesModel.URL_NOT_VALID.format(param_name=param_name, value=value)

  return check


def valid_uuid(param_name: str = 'parameter', position: int = 0) -> GuardFunction:
  """
  Validates that a parameter is a valid UUID format.

  Args:
      param_name: Name of the parameter to validate
      position: Position of parameter in function args

  Returns:
      Guard function that returns True if parameter is valid UUID format
  """

  def check(*args: Any, **kwargs: Any) -> Union[bool, str]:
    value = extract_param(param_name, position, args, kwargs)
    
    if not isinstance(value, str):
      return f"Parameter '{param_name}' must be a string"
    
    if UUID_PATTERN.match(value):
      return True
    
    return f"{param_name} must be a valid UUID format: {value}"

  return check


def valid_file_path(
  param_name: str = 'parameter', 
  position: int = 0,
  must_exist: bool = True,
  must_be_file: bool = False,
  must_be_dir: bool = False
) -> GuardFunction:
  """
  Validates that a parameter is a valid file path.

  Args:
      param_name: Name of the parameter to validate
      position: Position of parameter in function args
      must_exist: Whether the file must actually exist on the filesystem
      must_be_file: Whether the path must be a file (not directory)
      must_be_dir: Whether the path must be a directory (not file)

  Returns:
      Guard function that returns True if parameter is valid file path
  """

  def check(*args: Any, **kwargs: Any) -> Union[bool, str]:
    value = extract_param(param_name, position, args, kwargs)
    
    if not isinstance(value, (str, Path)):
      return f"Parameter '{param_name}' must be a string or Path object"
    
    path = Path(value)
    
    if must_exist and not path.exists():
      return ErrorMessagesModel.PATH_MUST_EXIST.format(param_name=param_name, value=value)
    
    # Check file/directory type if specified
    if must_exist:
      if must_be_file and not path.is_file():
        return ErrorMessagesModel.PATH_MUST_BE_FILE.format(param_name=param_name, value=value)
      if must_be_dir and not path.is_dir():
        return ErrorMessagesModel.PATH_MUST_BE_DIR.format(param_name=param_name, value=value)
    
    # Basic path validation - check if it's a reasonable path format
    try:
      # This will raise an exception for invalid path characters
      path.resolve()
      return True
    except (OSError, ValueError):
      return f"Parameter '{param_name}' is not a valid file path format: {value}"

  return check