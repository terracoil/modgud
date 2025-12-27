"""Port definition for building injection parameter maps."""

from typing import Callable, Dict, Protocol, Type, runtime_checkable

from .injectable_detector_port import InjectableDetectorPort


@runtime_checkable
class InjectionMapBuilderPort(Protocol):
  """Port for building injection parameter maps."""

  def build_injection_map(
    self, func: Callable, detector: InjectableDetectorPort
  ) -> Dict[str, Type]:
    """
    Build a map of parameters that need injection.

    :param func: Function to analyze
    :param detector: Injectable detector to use
    :return: Map of parameter names to types
    """
    ...

  def merge_with_provided(
    self, injection_map: Dict[str, Type], provided_args: tuple, provided_kwargs: dict
  ) -> Dict[str, Type]:
    """
    Remove already-provided parameters from injection map.

    :param injection_map: Full injection map
    :param provided_args: Positional arguments provided
    :param provided_kwargs: Keyword arguments provided
    :return: Filtered injection map
    """
    ...
