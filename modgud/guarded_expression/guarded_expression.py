"""Unified guarded_expression decorator combining guards and implicit returns.

Unified guarded_expression decorator that combines guard clause validation
with optional implicit return transformation.

This is the primary decorator for the modgud library, unifying the functionality
of guard_clause and implicit_return into a single, composable decorator.
"""

import functools
import inspect
from textwrap import dedent
from typing import Any, Callable, Optional

from ..shared.errors import GuardClauseError, UnsupportedConstructError
from ..shared.types import FailureBehavior, GuardFunction
from .implicit_return import apply_implicit_return_transform
from .guard_runtime import check_guards, handle_failure


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
          - Callable: Invoked with (error_msg, *args, **kwargs), return value used
          - Exception class: Instantiated with error message and raised
      log: If True, log guard failures at INFO level (default: False)

  Usage:
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
        implicit_return: Enable implicit return transformation
        on_error: Behavior on guard failure
        log: Enable logging of guard failures

    """
    self.guards = guards
    self.implicit_return_enabled = implicit_return
    self.on_error = on_error
    self.log = log

  def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
    """Apply guard wrapping and optional implicit return transformation."""
    return (
      self._apply_implicit_return(func)
      if self.implicit_return_enabled
      else self._wrap_with_guards(func)
    )

  def _apply_implicit_return(self, func: Callable[..., Any]) -> Callable[..., Any]:
    """Apply implicit return transformation to the function."""
    # Extract and parse source
    try:
      source = dedent(inspect.getsource(func))
    except OSError as e:
      raise UnsupportedConstructError(
        'Source unavailable — guarded_expression with implicit_return=True requires importable source code.'
      ) from e

    # Transform the AST
    new_tree, filename = apply_implicit_return_transform(source, func.__name__)

    # Compile the transformed code in the original global scope
    env = func.__globals__.copy()
    code = compile(new_tree, filename=filename, mode='exec')
    exec(code, env)

    transformed = env[func.__name__]

    # Wrap with guards and return
    return self._wrap_with_guards(transformed, preserve_metadata_from=func)

  def _wrap_with_guards(
    self, func: Callable[..., Any], preserve_metadata_from: Optional[Callable[..., Any]] = None
  ) -> Callable[..., Any]:
    """Wrap the function with guard checking logic."""
    metadata_source = preserve_metadata_from if preserve_metadata_from is not None else func

    @functools.wraps(metadata_source)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
      # Check guards if any are defined
      if self.guards:
        error_msg = check_guards(self.guards, args, kwargs)
        if error_msg is not None:
          # Handle failure
          result, exception_to_raise = handle_failure(
            error_msg, self.on_error, func.__name__, args, kwargs, self.log
          )
          # Raise exception if configured
          if exception_to_raise:
            raise exception_to_raise
          return result

      # All guards passed - execute the function
      return func(*args, **kwargs)

    # Preserve explicit annotations for typing/IDE help
    wrapper.__signature__ = inspect.signature(metadata_source)  # type: ignore[attr-defined]
    wrapper.__annotations__ = getattr(metadata_source, '__annotations__', {})
    return wrapper
