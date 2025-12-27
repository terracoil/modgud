"""Port definition for detecting injectable parameters."""

from typing import Any, Callable, Dict, Protocol, Type, runtime_checkable


@runtime_checkable
class InjectableDetectorPort(Protocol):
  """Port for detecting injectable parameters."""

  def is_injectable(self, param_type: Any) -> bool:
    """
    Determine if a type should be dependency injected.

    :param param_type: The parameter type annotation
    :return: True if the type should be injected
    """
    ...

  def get_injectable_params(self, func: Callable) -> Dict[str, Type]:
    """
    Extract injectable parameters from a function signature.

    :param func: Function to analyze
    :return: Dictionary mapping parameter names to their types
    """
    ...

  def is_protocol(self, param_type: Any) -> bool:
    """
    Check if a type is a Protocol.

    :param param_type: The type to check
    :return: True if it's a Protocol
    """
    ...
