"""
Inject decorator for dependency injection.

This module provides the Inject decorator that enables automatic dependency
injection into function parameters following the single class per file principle.
"""

import functools
import inspect
from typing import Any, Callable, Dict, Optional, Type, TypeVar, get_type_hints

from ...domain.exceptions import DependencyInjectionError, ServiceNotFoundError
from ..core.di import EnergyInverter

T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])


class Inject:
  """
  Decorator for automatic dependency injection into function parameters.

  Injects services based on parameter type annotations or explicit interface specifications.
  Integrates seamlessly with other modgud decorators for composition.

  Usage:
      @Inject(IEmailService)
      def send_welcome_email(email_service: IEmailService, user: User) -> None:
          email_service.send(user.email, "Welcome!")

      # Auto-injection based on type hints
      @Inject.auto()
      def process_order(payment_service: IPaymentService, order: Order) -> None:
          payment_service.charge(order.total)
  """

  def __init__(self, *interfaces: Type, service_names: Optional[Dict[str, str]] = None) -> None:
    """
    Initialize the inject decorator.

    Args:
        *interfaces: Interface types to inject (in parameter order)
        service_names: Optional mapping of parameter names to service names

    """
    self.interfaces = interfaces
    self.service_names = service_names or {}
    self.auto_inject = False

  @classmethod
  def auto(cls, service_names: Optional[Dict[str, str]] = None) -> 'Inject':
    """
    Create an auto-injection decorator that uses type hints.

    Args:
        service_names: Optional mapping of parameter names to service names

    Returns:
        Inject decorator configured for auto-injection

    """
    instance = cls(service_names=service_names)
    instance.auto_inject = True
    return instance

  def __call__(self, func: F) -> F:
    """
    Apply dependency injection to the function.

    Args:
        func: Function to decorate

    Returns:
        Decorated function with dependency injection

    """
    # Get function signature and type hints
    sig = inspect.signature(func)
    type_hints = get_type_hints(func)

    # Determine injection strategy
    if self.auto_inject:
      injection_map = self._build_auto_injection_map(sig, type_hints)
    else:
      injection_map = self._build_explicit_injection_map(sig)

    # Create the wrapper function
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
      # Bind arguments to get parameter names
      bound_args = sig.bind_partial(*args, **kwargs)
      bound_args.apply_defaults()

      # Inject dependencies for missing parameters
      injected_kwargs = {}
      di = EnergyInverter.instance()

      for param_name, interface_type in injection_map.items():
        if param_name not in bound_args.arguments:
          service_name = self.service_names.get(param_name, 'default')
          try:
            injected_service = di.resolve(interface_type, service_name)
            injected_kwargs[param_name] = injected_service
          except ServiceNotFoundError as e:
            raise DependencyInjectionError(
              f"Cannot inject dependency for parameter '{param_name}' of type {interface_type.__name__}: {e}"
            ) from e

      # Merge injected dependencies with provided kwargs
      final_kwargs = {**kwargs, **injected_kwargs}

      # Call the original function
      return func(*args, **final_kwargs)

    # Preserve function metadata
    wrapper.__signature__ = sig  # type: ignore[attr-defined]
    wrapper.__annotations__ = getattr(func, '__annotations__', {})

    # Mark as dependency-injected for introspection
    wrapper.__dependency_injected__ = True  # type: ignore[attr-defined]
    wrapper.__injection_map__ = injection_map  # type: ignore[attr-defined]

    return wrapper  # type: ignore[return-value]

  def _build_auto_injection_map(
    self, sig: inspect.Signature, type_hints: Dict[str, Any]
  ) -> Dict[str, Type]:
    """
    Build injection map using type hints for auto-injection.

    Args:
        sig: Function signature
        type_hints: Type hints for the function

    Returns:
        Mapping of parameter names to interface types

    """
    injection_map = {}

    for param_name, param in sig.parameters.items():
      # Skip self/cls parameters
      if param_name in ('self', 'cls'):
        continue

      # Skip parameters with default values (unless they're None)
      if param.default is not inspect.Parameter.empty and param.default is not None:
        continue

      # Check if parameter has a type hint
      if param_name in type_hints:
        param_type = type_hints[param_name]

        # Only inject if the type looks like an interface
        if self._is_injectable_type(param_type):
          injection_map[param_name] = param_type

    return injection_map

  def _build_explicit_injection_map(self, sig: inspect.Signature) -> Dict[str, Type]:
    """
    Build injection map using explicitly provided interfaces.

    Args:
        sig: Function signature

    Returns:
        Mapping of parameter names to interface types

    """
    injection_map = {}
    param_names = [name for name in sig.parameters.keys() if name not in ('self', 'cls')]

    for i, interface_type in enumerate(self.interfaces):
      if i < len(param_names):
        param_name = param_names[i]
        injection_map[param_name] = interface_type

    return injection_map

  def _is_injectable_type(self, param_type: Any) -> bool:
    """
    Check if a type is suitable for dependency injection.

    Args:
        param_type: Type to check

    Returns:
        True if the type should be injected

    """
    # Skip built-in types and common non-injectable types
    if param_type in (str, int, float, bool, list, dict, tuple, set):
      return False

    # Skip Optional types unless they wrap an injectable type
    if hasattr(param_type, '__origin__'):
      if param_type.__origin__ is type(None):  # Optional[T]
        return False

    # Check if it looks like a Protocol or ABC
    if hasattr(param_type, '_is_protocol') or hasattr(param_type, '__abstractmethods__'):
      return True

    # For classes, check if they look like interfaces (abstract or protocol-like)
    if inspect.isclass(param_type):
      # If it has abstract methods, likely an interface
      if hasattr(param_type, '__abstractmethods__') and param_type.__abstractmethods__:
        return True

      # If class name starts with 'I' and is uppercase, likely an interface
      if (
        param_type.__name__.startswith('I')
        and len(param_type.__name__) > 1
        and param_type.__name__[1].isupper()
      ):
        return True

    return False


# Convenient function-style decorators
def inject(*interfaces: Type, service_names: Optional[Dict[str, str]] = None) -> Callable[[F], F]:
  """
  Function-style decorator for explicit dependency injection.

  Args:
      *interfaces: Interface types to inject
      service_names: Optional service name mappings

  Returns:
      Decorator function

  """
  return Inject(*interfaces, service_names=service_names)


def inject_auto(service_names: Optional[Dict[str, str]] = None) -> Callable[[F], F]:
  """
  Function-style decorator for auto dependency injection.

  Args:
      service_names: Optional service name mappings

  Returns:
      Decorator function

  """
  return Inject.auto(service_names=service_names)
