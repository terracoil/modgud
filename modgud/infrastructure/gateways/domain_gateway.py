"""
Domain gateway for clean access to domain layer components.

Provides a clean, controlled access point to domain layer functionality
while maintaining proper layer isolation and dependency inversion.
"""

from ...domain.models.error_messages_model import ErrorMessagesModel
from ...domain.models.info_messages_model import InfoMessagesModel
from ...domain.models.types import GuardFunction, FailureBehavior


class DomainGateway:
  """Clean access to domain layer components."""
  
  @staticmethod
  def get_error_messages() -> ErrorMessagesModel:
    """
    Get domain error messages model.
    
    Returns:
        ErrorMessagesModel instance for error message templating
    """
    return ErrorMessagesModel()
  
  @staticmethod
  def get_info_messages() -> InfoMessagesModel:
    """
    Get domain info messages model.
    
    Returns:
        InfoMessagesModel instance for informational message templating
    """
    return InfoMessagesModel()
  
  @staticmethod
  def create_guard_function(validation_logic, error_message: str) -> GuardFunction:
    """
    Create a properly formatted guard function.
    
    Args:
        validation_logic: Function that returns True if valid, False otherwise
        error_message: Error message to return on validation failure
        
    Returns:
        Guard function with proper signature
    """
    def guard(*args, **kwargs):
      if validation_logic(*args, **kwargs):
        return True
      return error_message
    
    return guard