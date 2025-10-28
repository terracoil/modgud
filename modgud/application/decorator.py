"""
Unified guarded_expression decorator combining guards and implicit returns.

This is the primary decorator for the modgud library, using infrastructure
services via LPA architecture with strict layer boundaries.

Application layer only imports from infrastructure layer gateway.
"""

import functools
import inspect
from typing import Any, Callable, Optional

from ..infrastructure import (
  # Domain types/errors (re-exported by infrastructure)
  FailureBehavior,
  GuardClauseError,
  GuardFunction,
  # Default service implementations
  GuardService,
  # Infrastructure service ports
  GuardServicePort,
  TransformService,
  TransformServicePort,
  UnsupportedConstructError,
)


class guarded_expression:
  """
  Unified decorator combining guard clauses with optional implicit return.

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
      guard_service: Optional GuardServicePort implementation (uses default if not provided)
      transform_service: Optional TransformServicePort implementation (uses default if not provided)

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
    guard_service: Optional[GuardServicePort] = None,
    transform_service: Optional[TransformServicePort] = None,
  ):
    """
    Initialize the guarded_expression decorator.

    Args:
        *guards: Variable number of guard functions
        implicit_return: Enable implicit return transformation
        on_error: Behavior on guard failure
        log: Enable logging of guard failures
        guard_service: Optional service for guard operations (uses default if None)
        transform_service: Optional service for transformation operations (uses default if None)

    """
    self.guards = guards
    self.implicit_return_enabled = implicit_return
    self.on_error = on_error
    self.log = log

    # Dependency injection with lazy defaults
    self._guard_service = guard_service
    self._transform_service = transform_service

  @property
  def guard_service(self) -> GuardServicePort:
    """Get guard service implementation, lazily loading default if needed."""
    if self._guard_service is None:
      self._guard_service = GuardService()
    return self._guard_service

  @property
  def transform_service(self) -> TransformServicePort:
    """Get transform service implementation, lazily loading default if needed."""
    if self._transform_service is None:
      self._transform_service = TransformService()
    return self._transform_service

  def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
    """Apply guard wrapping and optional implicit return transformation."""
    # Transform first if needed, then wrap - transformation changes function body
    return (
      self._apply_implicit_return(func)
      if self.implicit_return_enabled
      else self._wrap_with_guards(func)
    )

  def _apply_implicit_return(self, func: Callable[..., Any]) -> Callable[..., Any]:
    """Apply implicit return transformation to the function using transform service."""
    # Validate source availability
    try:
      inspect.getsource(func)
    except OSError as e:
      raise UnsupportedConstructError(
        'Source unavailable — guarded_expression with implicit_return=True requires importable source code.'
      ) from e

    # Transform using infrastructure service
    transformed = self.transform_service.transform_to_implicit_return(func, func.__name__)

    # Wrap with guards and return
    return self._wrap_with_guards(transformed, preserve_metadata_from=func)

  def _wrap_with_guards(
    self, func: Callable[..., Any], preserve_metadata_from: Optional[Callable[..., Any]] = None
  ) -> Callable[..., Any]:
    """Wrap the function with guard checking logic using guard service."""
    # Use original for metadata when transforming - transformed lacks source context
    metadata_source = preserve_metadata_from if preserve_metadata_from is not None else func

    @functools.wraps(metadata_source)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
      # Check guards if any are defined
      if self.guards:
        # Validate using infrastructure service
        success, result, exception = self.guard_service.validate_inputs(
          self.guards, args, kwargs, self.on_error, self.log
        )

        if not success:
          # Exception path prioritized for clean error propagation
          if exception:
            raise exception
          return result

      # All guards passed - execute the function
      return func(*args, **kwargs)

    # Preserve signature for IDE autocomplete and runtime introspection
    wrapper.__signature__ = inspect.signature(metadata_source)  # type: ignore[attr-defined]
    wrapper.__annotations__ = getattr(metadata_source, '__annotations__', {})
    return wrapper
