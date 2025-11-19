"""
Safe expression factory for creating safe expression decorators.

This module provides the SafeExpressionFactory class for creating safe expression decorators,
following the single class per file principle.
"""

from typing import Callable, TypeVar, Union

from ..decorator.safe_expression_decorator import SafeExpressionDecorator
from ..results.result_base import Result

T = TypeVar('T')


class SafeExpressionFactory:
  """
  Factory class for creating safe expression decorators.

  This class encapsulates the creation of safe expression decorators
  following the single class per file and class encapsulation principles.
  """

  @staticmethod
  def create_decorator(
    catch_exceptions: tuple[type[Exception], ...] = (Exception,), convert_none: bool = False
  ) -> SafeExpressionDecorator:
    """
    Create a safe expression decorator with specified options.

    Args:
        catch_exceptions: Tuple of exception types to catch
        convert_none: If True, convert None results to Err

    Returns:
        SafeExpressionDecorator instance

    """
    return SafeExpressionDecorator(catch_exceptions=catch_exceptions, convert_none=convert_none)

  @staticmethod
  def safe_expression(
    func: Callable[..., T] | None = None,
    *,
    catch_exceptions: tuple[type[Exception], ...] = (Exception,),
    convert_none: bool = False,
  ) -> Union[Callable[..., Result[T, Exception]], SafeExpressionDecorator]:
    """
    Create a safe expression decorator that can be used with or without parameters.

    This method provides the convenient @safe_expression decorator interface
    while maintaining proper class encapsulation.

    Examples:
        @SafeExpressionFactory.safe_expression
        def divide(a, b):
            return a / b

        @SafeExpressionFactory.safe_expression(catch_exceptions=(ZeroDivisionError,))
        def safe_divide(a, b):
            return a / b

    Args:
        func: Function to decorate (when used without parameters)
        catch_exceptions: Tuple of exception types to catch
        convert_none: If True, convert None results to Err

    Returns:
        Decorated function or decorator instance

    """
    result = None
    if func is None:
      # Called with parameters: @safe_expression(...)
      result = SafeExpressionDecorator(catch_exceptions=catch_exceptions, convert_none=convert_none)
    else:
      # Called without parameters: @safe_expression
      decorator = SafeExpressionDecorator()
      result = decorator(func)
    return result
