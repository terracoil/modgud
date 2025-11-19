"""
Domain type definitions for modgud.

All type aliases and type definitions used throughout the modgud library
are defined here following domain-driven design principles. The domain 
layer is passive and contains no business logic - only type definitions.
"""

from typing import Any, Callable, Union

__all__ = [
  'GuardFunction',
  'FailureTypes',
  'FailureBehavior',
]

# Guard function signature: (*args, **kwargs) -> True | str
# Guards return True for success, or an error message string for failure
GuardFunction = Callable[..., Union[bool, str]]

# Primitive failure return types
FailureTypes = Union[bool, str, int, float, None, dict[str, Any], list[Any], tuple[Any, ...]]

# Complete failure behavior types including callables and exception classes
FailureBehavior = Union[FailureTypes, Callable[..., Any], type]