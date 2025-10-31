"""
Validation protocol for cross-layer validation contracts.

Defines the contract for validation operations across layer boundaries,
providing a clear interface for validation logic that can be implemented
by different layers according to their needs.
"""

from typing import List, Protocol

from ...domain.models.types import GuardFunction


class ValidationResult:
  """Result of validation operation."""
  
  def __init__(self, success: bool, error_message: str = "", context: dict = None):
    self.success = success
    self.error_message = error_message
    self.context = context or {}


class ValidationProtocol(Protocol):
  """Cross-layer validation contract."""
  
  def validate_guards(self, guards: List[GuardFunction]) -> ValidationResult:
    """
    Validate a list of guard functions.
    
    Args:
        guards: List of guard functions to validate
        
    Returns:
        ValidationResult indicating success or failure with details
    """
    ...
  
  def validate_parameters(self, args: tuple, kwargs: dict) -> ValidationResult:
    """
    Validate function parameters.
    
    Args:
        args: Positional arguments to validate
        kwargs: Keyword arguments to validate
        
    Returns:
        ValidationResult indicating success or failure with details
    """
    ...