"""Service implementing InjectableDetectorPort for detecting injectable parameters."""

import inspect
from typing import Any, Callable, Dict, Type, get_type_hints


class InjectableDetectorService:
  """Service for detecting injectable parameters."""

  def is_injectable(self, param_type: Any) -> bool:
    """Determine if a type should be dependency injected.

    :param param_type: The parameter type annotation
    :return: True if the type should be injected
    """
    # Skip built-in types
    if param_type in (str, int, float, bool, list, dict, tuple, set, type(None)):
      return False

    # Skip Any and generic types
    if param_type is Any:
      return False

    # Check if it's a Protocol
    if self.is_protocol(param_type):
      return True

    # Check if it's a class (but not a built-in)
    if isinstance(param_type, type):
      # Skip if it's from builtins module
      module = getattr(param_type, '__module__', None)
      if module and module in ('builtins', '__builtin__'):
        return False
      return True

    return False

  def get_injectable_params(self, func: Callable) -> Dict[str, Type]:
    """Extract injectable parameters from a function signature.

    :param func: Function to analyze
    :return: Dictionary mapping parameter names to their types
    """
    injectable_params = {}

    # Get type hints
    try:
      hints = get_type_hints(func)
    except Exception:
      # If we can't get type hints, fall back to signature inspection
      hints = {}

    # Get signature
    sig = inspect.signature(func)

    for param_name, param in sig.parameters.items():
      # Skip *args and **kwargs
      if param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
        continue

      # Get type from hints or annotation
      param_type = hints.get(param_name, param.annotation)

      # Skip if no type annotation
      if param_type is inspect.Parameter.empty:
        continue

      # Check if injectable
      if self.is_injectable(param_type):
        injectable_params[param_name] = param_type

    return injectable_params

  def is_protocol(self, param_type: Any) -> bool:
    """Check if a type is a Protocol.

    :param param_type: The type to check
    :return: True if it's a Protocol
    """
    # Check if it's a Protocol subclass
    if hasattr(param_type, '__class__'):
      mro = getattr(param_type.__class__, '__mro__', ())
      for base in mro:
        if base.__name__ == 'Protocol':
          return True

    # Check if it has _is_protocol attribute (runtime_checkable protocols)
    if hasattr(param_type, '_is_protocol'):
      return True

    # Check if it's decorated with @runtime_checkable
    if hasattr(param_type, '__protocol_attrs__'):
      return True

    return False
