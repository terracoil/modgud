"""
Unified guarded_expression decorator combining guards and implicit returns.

Unified guarded_expression decorator that combines guard clause validation
with optional implicit return transformation.

This is the primary decorator for the modgud library, unifying the functionality
of guard_clause and implicit_return into a single, composable decorator.
"""

import warnings
from typing import Any, Callable

from modgud.domain import (
  FailureBehavior,
  GuardClauseError,
  GuardFunction,
  UnsupportedConstructError,
)
from modgud.domain.ports import GuardWrapperPort, ImplicitReturnTransformerPort
from modgud.infrastructure.service_locator import get_service_locator


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

    # Get services from service locator
    locator = get_service_locator()
    self._guard_wrapper = locator.resolve(GuardWrapperPort)
    self._implicit_transformer = locator.resolve(ImplicitReturnTransformerPort)

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
        transformed = self._implicit_transformer.transform_function(func)
        wrapped = self._guard_wrapper.wrap_function(
          transformed, self.guards, self.on_error, self.log
        )
        # Mark as implicit return for compatibility
        wrapped.__implicit_return__ = True  # type: ignore[attr-defined]
        return wrapped
      except (UnsupportedConstructError, ValueError, OSError):
        # Function may have already been transformed or source is unavailable
        # In either case, just wrap with guards
        wrapped = self._guard_wrapper.wrap_function(func, self.guards, self.on_error, self.log)
        # Still mark as implicit return enabled even if transformation failed
        wrapped.__implicit_return__ = True  # type: ignore[attr-defined]
        return wrapped
    else:
      return self._guard_wrapper.wrap_function(func, self.guards, self.on_error, self.log)
