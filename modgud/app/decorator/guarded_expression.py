"""Unified guarded_expression decorator combining guards and implicit returns.

Unified guarded_expression decorator that combines guard clause validation
with optional implicit return transformation.

This is the primary decorator for the modgud library, unifying the functionality
of guard_clause and implicit_return into a single, composable decorator.
"""

from typing import Any, Callable

from modgud.domain import (
  FailureBehavior,
  GuardClauseError,
  GuardFunction,
  UnsupportedConstructError,
)
from modgud.infrastructure import GuardRuntime
from modgud.infrastructure.transform import ImplicitReturnTransformer


class guarded_expression:
  """Unified decorator combining guard clauses with optional implicit return.

  Guards are callables that return True (pass) or a string error message (fail).
  On failure, behavior is determined by the `on_error` parameter.

  Default behavior: Raises GuardClauseError on guard failure.

  Args:
      *guards: Guard functions returning True or error message string
      implicit_return: Enable implicit return transformation (default: True)
      on_error: Failure behavior (default: GuardClauseError) - can be:
          - Value (str, int, None, etc.): Returned on guard failure
          - Callable: Invoked with (error_msg, *args, **kwargs), return name used
          - Exception class: Instantiated with error message and raised
      log: If True, log guard failures at INFO level (default: False)

  Usage (with separate decorators):
      from modgud import implicit_return, guarded_expression

      @implicit_return
      @guarded_expression(
          lambda x: x > 0 or "Must be positive"
      )
      def safe_divide(x):
          result = 100 / x
          result  # No explicit return needed

  Usage (with implicit_return parameter):
      @guarded_expression(
          lambda x: x > 0 or "Must be positive",
          implicit_return=True,
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
    """Initialize the guarded_expression decorator.

    Args:
        *guards: Variable number of guard functions
        implicit_return: Enable implicit return transformation (default: True)
        on_error: Behavior on guard failure
        log: Enable logging of guard failures

    """
    self.guards = guards
    self.implicit_return_enabled = implicit_return
    self.on_error = on_error
    self.log = log

  def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
    """Apply guard wrapping and optional implicit return transformation."""
    target = func
    if self.implicit_return_enabled:
      try:
        target = ImplicitReturnTransformer.transform_function(func)
      except (UnsupportedConstructError, ValueError, OSError):
        pass
    wrapped = GuardRuntime.wrap_function(target, self.guards, self.on_error, self.log)
    if self.implicit_return_enabled:
      wrapped.__implicit_return__ = True  # type: ignore[attr-defined]
    return wrapped
