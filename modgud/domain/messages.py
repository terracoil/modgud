"""
Domain message templates for modgud.

Centralized error and validation message templates following domain-driven
design principles. The domain layer is passive and contains no business
logic - only message template definitions.

This module re-exports message templates from their individual files
following the single class per file principle.
"""

from .error_messages import ErrorMessages
from .info_messages import InfoMessages

__all__ = [
  'ErrorMessages',
  'InfoMessages',
]
