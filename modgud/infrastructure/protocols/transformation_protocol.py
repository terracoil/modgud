"""
Transformation protocol for cross-layer AST transformation contracts.

Defines the contract for AST transformation operations across layer boundaries,
providing a clear interface for function transformation logic.
"""

from typing import Any, Callable, Protocol


class TransformationResult:
  """Result of transformation operation."""
  
  def __init__(self, function: Callable[..., Any], metadata: dict = None):
    self.function = function
    self.metadata = metadata or {}


class TransformationProtocol(Protocol):
  """Cross-layer transformation contract."""
  
  def transform_function(self, func: Callable[..., Any], options: dict) -> TransformationResult:
    """
    Transform a function according to specified options.
    
    Args:
        func: Original function to transform
        options: Transformation options and configuration
        
    Returns:
        TransformationResult containing transformed function and metadata
    """
    ...
  
  def validate_transformation(self, original: Callable[..., Any], transformed: Callable[..., Any]) -> bool:
    """
    Validate that transformation preserved essential characteristics.
    
    Args:
        original: Original function before transformation
        transformed: Function after transformation
        
    Returns:
        True if transformation is valid, False otherwise
    """
    ...