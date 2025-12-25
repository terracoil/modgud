"""
ServiceLifetime enum for modgud domain layer.

Enumeration for dependency injection service lifetimes following domain-driven
design principles. The domain layer is passive and contains no business logic
- only enumeration definitions.
"""

from enum import Enum, auto

__all__ = ['ServiceLifetime']


class ServiceLifetime(Enum):
  """Lifetime strategy for dependency injection services."""

  SINGLETON = auto()  # Single instance per container
  TRANSIENT = auto()  # New instance per request
  SCOPED = auto()  # Single instance per scope/request context
