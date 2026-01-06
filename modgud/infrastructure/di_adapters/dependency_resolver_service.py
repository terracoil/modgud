"""Service implementing DependencyResolverPort for dependency resolution."""

import functools
import inspect
from typing import Any, Callable, Dict

from ...domain.ports import (
  DIContainerPort,
  InjectableDetectorPort,
)


class DependencyResolverService:
  """Service for resolving dependencies and creating injection wrappers."""

  def __init__(self, detector: InjectableDetectorPort) -> None:
    """
    Initialize with an injectable detector.

    :param detector: Injectable detector service
    """
    self._detector = detector

  def resolve_dependencies(self, func: Callable, container: DIContainerPort) -> Dict[str, Any]:
    """
    Resolve all dependencies for a function.

    :param func: Function with dependencies
    :param container: DI container to resolve from
    :return: Dictionary mapping parameter names to resolved instances
    """
    resolved = {}
    injectable_params = self._detector.get_injectable_params(func)

    for param_name, param_type in injectable_params.items():
      try:
        # Try to resolve from container
        resolved[param_name] = container.resolve(param_type)
      except KeyError:
        # If not found, skip - will be handled by wrapper
        pass

    return resolved

  def create_injection_wrapper(self, func: Callable, container: DIContainerPort) -> Callable:
    """
    Create a wrapper that injects dependencies.

    :param func: Function to wrap
    :param container: DI container to use
    :return: Wrapped function with automatic injection
    """
    # Get injectable parameters
    injectable_params = self._detector.get_injectable_params(func)

    if not injectable_params:
      # No injectable params, return original function
      return func

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
      # Get function signature
      sig = inspect.signature(func)
      bound_args = sig.bind_partial(*args, **kwargs)
      bound_args.apply_defaults()

      # Inject missing dependencies
      for param_name, param_type in injectable_params.items():
        if param_name not in bound_args.arguments:
          try:
            # Resolve from container
            bound_args.arguments[param_name] = container.resolve(param_type)
          except KeyError:
            # If the parameter has a default name, use it
            param = sig.parameters.get(param_name)
            if param and param.default is not inspect.Parameter.empty:
              bound_args.arguments[param_name] = param.default
            # Otherwise, let it fail naturally when calling the function

      # Call with injected dependencies
      return func(**bound_args.arguments)

    # Preserve metadata
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__dict__.update(func.__dict__)

    return wrapper
