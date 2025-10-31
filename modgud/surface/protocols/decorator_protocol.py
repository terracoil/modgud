"""
Decorator protocol for surface layer contracts.

Defines the contract for decorator implementations in the surface layer,
ensuring consistent interfaces for different decorator types and behaviors.
"""

from typing import Any, Callable, Protocol, Tuple

from ...domain.models.types import GuardFunction, FailureBehavior


class DecoratorProtocol(Protocol):
  """Contract for decorator implementations."""
  
  def apply_guards(self, func: Callable[..., Any], guards: Tuple[GuardFunction, ...]) -> Callable[..., Any]:
    """
    Apply guard validation to a function.
    
    Args:
        func: Function to decorate with guards
        guards: Tuple of guard functions to apply
        
    Returns:
        Decorated function with guard validation
    """
    ...
  
  def apply_transformation(self, func: Callable[..., Any], options: dict) -> Callable[..., Any]:
    """
    Apply transformation to a function.
    
    Args:
        func: Function to transform
        options: Transformation options
        
    Returns:
        Transformed function
    """
    ...
  
  def configure_failure_handling(self, on_error: FailureBehavior, log_enabled: bool) -> dict:
    """
    Configure failure handling options.
    
    Args:
        on_error: Failure behavior configuration
        log_enabled: Whether to enable logging
        
    Returns:
        Configuration dictionary for failure handling
    """
    ...