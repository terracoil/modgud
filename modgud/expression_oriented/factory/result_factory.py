"""
Result factory for creating Result instances.

This module provides the ResultFactory class for creating Result instances
and performing Result operations, following the single class per file principle.
"""

from typing import Callable, TypeVar

from ..results.err_result import Err
from ..results.ok_result import Ok
from ...domain.result_protocol import ResultProtocol as Result

T = TypeVar('T')
E = TypeVar('E')


class ResultFactory:
  """
  Factory class for creating and manipulating Result instances.

  This class encapsulates all Result-related operations following the
  single class per file and class encapsulation principles.
  """

  @staticmethod
  def ok(value: T) -> Result[T, E]:
    """
    Create an Ok result with the given value.

    Args:
        value: The success value to wrap

    Returns:
        Ok result containing the value

    """
    return Ok(value)

  @staticmethod
  def err(error: E) -> Result[T, E]:
    """
    Create an Err result with the given error.

    Args:
        error: The error value to wrap

    Returns:
        Err result containing the error

    """
    return Err(error)

  @staticmethod
  def from_exception(func: Callable[[], T]) -> Result[T, Exception]:
    """
    Execute a function and wrap the result in a Result type.

    Args:
        func: Function to execute

    Returns:
        Ok with the result if successful, Err with the exception if it fails

    """
    result = None
    try:
      value = func()
      result = Ok(value)
    except Exception as e:
      result = Err(e)
    return result

  @staticmethod
  def from_optional(value: T | None, error_message: str = 'Value is None') -> Result[T, str]:
    """
    Create a Result from an optional value.

    Args:
        value: Value that may be None
        error_message: Error message if value is None

    Returns:
        Ok with value if not None, otherwise Err with error message

    """
    result = None
    if value is not None:
      result = Ok(value)
    else:
      result = Err(error_message)
    return result
