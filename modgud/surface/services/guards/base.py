"""
Base utilities for guard implementations.

Provides shared functionality like parameter extraction that all guard
modules can use to implement consistent behavior.
"""

from typing import Any, Optional


def extract_param(
  param_name: str,
  position: Optional[int],
  args: tuple[Any, ...],
  kwargs: dict[str, Any],
  default: Any = None,
) -> Any:
  """
  Extract parameter value from args or kwargs for custom guard implementations.

  This is a public utility function for authors writing custom guards who need to
  extract parameter values from function arguments.

  Args:
      param_name: Name of the parameter in kwargs
      position: Position in args (None defaults to position 0)
      args: Positional arguments tuple from guard function
      kwargs: Keyword arguments dict from guard function
      default: Default value if parameter not found

  Returns:
      Parameter value from args[position] or kwargs[param_name] or default

  Example:
      # Extract 'amount' parameter from function arguments
      def validate_amount(*args, **kwargs):
          amount = extract_param('amount', 1, args, kwargs)
          return amount > 0
  """
  # Prefer keyword argument if available
  if param_name in kwargs:
    return kwargs[param_name]

  # Fall back to positional argument if position is provided and valid
  # If position is None, default to position 0
  actual_position = position if position is not None else 0
  if 0 <= actual_position < len(args):
    return args[actual_position]

  # Use default if provided, otherwise return None
  result: Any = default
  return result