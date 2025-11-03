"""
Unified guarded_expression decorator combining guards and implicit returns.

Unified guarded_expression decorator that combines guard clause validation
with optional implicit return transformation.

This is the primary decorator for the modgud library, unifying the functionality
of guard_clause and implicit_return into a single, composable decorator.
"""

import functools
import inspect
import warnings
from typing import Any, Callable

from .errors import GuardClauseError, UnsupportedConstructError
from .guard_runtime import GuardRuntime
from .implicit_return_decorator import implicit_return
from .types import FailureBehavior, GuardFunction


class guarded_expression:
  """
  Unified decorator combining guard clauses with optional implicit return.

  Guards are callables that return True (pass) or a string error message (fail).
  On failure, behavior is determined by the `on_error` parameter.

  Default behavior: Raises GuardClauseError on guard failure.

  Args:
      *guards: Guard functions returning True or error message string
      implicit_return: Enable implicit return transformation (default: True)
          DEPRECATED: Use @implicit_return decorator separately for composition
      on_error: Failure behavior (default: GuardClauseError) - can be:
          - Value (str, int, None, etc.): Returned on guard failure
          - Callable: Invoked with (error_msg, *args, **kwargs), return value used
          - Exception class: Instantiated with error message and raised
      log: If True, log guard failures at INFO level (default: False)

  Usage (recommended - with separate decorators):
      from modgud import implicit_return, guarded_expression

      @implicit_return
      @guarded_expression(
          lambda x: x > 0 or "Must be positive"
      )
      def safe_divide(x):
          result = 100 / x
          result  # No explicit return needed

  Usage (deprecated - with implicit_return parameter):
      @guarded_expression(
          lambda x: x > 0 or "Must be positive",
          implicit_return=True,  # DEPRECATED
          on_error=GuardClauseError
      )
      def safe_divide(x):
          result = 100 / x
          # No explicit return needed when implicit_return=True

  """

  def __init__(
    self,
    *guards: GuardFunction,
    implicit_return: bool = True,
    on_error: FailureBehavior = GuardClauseError,
    log: bool = False,
  ):
    """
    Initialize the guarded_expression decorator.

    Args:
        *guards: Variable number of guard functions
        implicit_return: Enable implicit return transformation (DEPRECATED - use @implicit_return decorator instead)
        on_error: Behavior on guard failure
        log: Enable logging of guard failures

    """
    self.guards = guards
    self.implicit_return_enabled = implicit_return
    self.on_error = on_error
    self.log = log

    # Issue deprecation warning if implicit_return parameter is used
    if implicit_return is not True:  # Only warn if explicitly set to False
      warnings.warn(
        "The 'implicit_return' parameter on @guarded_expression is deprecated and will be removed in v2.0.0. "
        'Use the @implicit_return decorator separately for explicit composition:\n'
        '  @implicit_return\n'
        '  @guarded_expression(guards...)\n'
        '  def my_function(): ...',
        DeprecationWarning,
        stacklevel=2,
      )

  def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
    """Apply guard wrapping and optional implicit return transformation."""
    # Apply implicit return first if enabled, then wrap with guards
    if self.implicit_return_enabled:
      try:
        # Try to apply implicit return transformation
        transformed = implicit_return(func)
        return self._wrap_with_guards(transformed)
      except UnsupportedConstructError:
        # Function may have already been transformed or source is unavailable
        # In either case, just wrap with guards
        return self._wrap_with_guards(func)
    else:
      return self._wrap_with_guards(func)

  def _wrap_with_guards(self, func: Callable[..., Any]) -> Callable[..., Any]:
    """Wrap the function with guard checking logic."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
      # Check guards if any are defined
      if self.guards:
        error_msg = GuardRuntime.check_guards(self.guards, args, kwargs)
        if error_msg is not None:
          # Handle failure
          result, exception_to_raise = GuardRuntime.handle_failure(
            error_msg, self.on_error, func.__name__, args, kwargs, self.log
          )
          # Exception path prioritized for clean error propagation
          if exception_to_raise:
            raise exception_to_raise
          return result

      # All guards passed - execute the function
      return func(*args, **kwargs)

    # Preserve signature for IDE autocomplete and runtime introspection
    wrapper.__signature__ = inspect.signature(func)  # type: ignore[attr-defined]
    wrapper.__annotations__ = getattr(func, '__annotations__', {})
    return wrapper
