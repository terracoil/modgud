"""
Guard combinators for composing complex validation logic.

Provides utilities for combining multiple guards with logical operations
and creating custom guard functions with flexible validation patterns.
"""

from typing import Any, Callable, List, Union

from ....infrastructure import GuardFunction


def all_of(*guards: GuardFunction) -> GuardFunction:
  """
  Creates a guard that passes only if ALL provided guards pass.

  Args:
      *guards: Variable number of guard functions to combine

  Returns:
      Guard function that returns True only if all guards pass

  Example:
      @guarded_expression(all_of(
          not_none('value'),
          positive('value'),
          in_range(1, 100, 'value')
      ))
      def process_value(value):
          return value * 2
  """

  def check(*args: Any, **kwargs: Any) -> Union[bool, str]:
    for guard in guards:
      result = guard(*args, **kwargs)
      if result is not True:
        return result  # Return first failure message
    return True

  return check


def any_of(*guards: GuardFunction) -> GuardFunction:
  """
  Creates a guard that passes if ANY of the provided guards pass.

  Args:
      *guards: Variable number of guard functions to combine

  Returns:
      Guard function that returns True if at least one guard passes

  Example:
      @guarded_expression(any_of(
          type_check(str, 'value'),
          type_check(int, 'value')
      ))
      def process_value(value):
          return str(value).upper()
  """

  def check(*args: Any, **kwargs: Any) -> Union[bool, str]:
    errors = []
    for guard in guards:
      result = guard(*args, **kwargs)
      if result is True:
        return True  # At least one guard passed
      errors.append(str(result))
    
    # All guards failed
    return f"All validation checks failed: {'; '.join(errors)}"

  return check


def custom(validation_func: Callable[..., bool], error_message: str) -> GuardFunction:
  """
  Creates a custom guard from a validation function and error message.

  Args:
      validation_func: Function that takes (*args, **kwargs) and returns bool
      error_message: Error message to return when validation fails

  Returns:
      Guard function that uses the custom validation logic

  Example:
      def is_even_number(*args, **kwargs):
          value = args[0] if args else kwargs.get('number', 0)
          return isinstance(value, int) and value % 2 == 0

      @guarded_expression(custom(is_even_number, "Number must be even"))
      def process_even(number):
          return number // 2
  """

  def check(*args: Any, **kwargs: Any) -> Union[bool, str]:
    if validation_func(*args, **kwargs):
      return True
    return error_message

  return check