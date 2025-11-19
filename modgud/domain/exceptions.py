"""
Domain exceptions for modgud.

All exception classes used throughout the modgud library are defined here
following domain-driven design principles. The domain layer is passive
and contains no business logic - only exception class definitions.
"""

from typing import Optional

__all__ = [
  'GuardClauseError',
  'ImplicitReturnError', 
  'ExplicitReturnDisallowedError',
  'MissingImplicitReturnError',
  'UnsupportedConstructError',
  'DependencyInjectionError',
  'ServiceNotFoundError',
]


class GuardClauseError(Exception):
  """Exception raised when a guard clause fails."""
  
  pass


class ImplicitReturnError(SyntaxError):
  """Base class for implicit-return related transformation errors."""

  def __init__(
    self, message: str, lineno: Optional[int] = None, col_offset: Optional[int] = None
  ) -> None:
    """
    Initialize the ImplicitReturnError with location information.

    :param message: Error message describing the issue
    :type message: str
    :param lineno: Line number where the error occurred  
    :type lineno: Optional[int]
    :param col_offset: Column offset where the error occurred
    :type col_offset: Optional[int]
    """
    super().__init__(message)
    if lineno is not None:
      self.lineno = lineno
    if col_offset is not None:
      self.offset = col_offset


class ExplicitReturnDisallowedError(ImplicitReturnError):
  """Raised when an explicit `return` statement is found in a decorated function."""
  
  pass


class MissingImplicitReturnError(ImplicitReturnError):
  """
  Raised when block cannot yield a value.

  Raised when a block is required to yield a value but does not end with
  a (convertible) final expression or a supported branching structure.
  """
  
  pass


class UnsupportedConstructError(ImplicitReturnError):
  """Raised when an unsupported AST construct appears at a required return boundary."""
  
  pass


class DependencyInjectionError(Exception):
  """Raised when dependency injection fails."""
  
  pass


class ServiceNotFoundError(Exception):
  """Raised when a requested service cannot be found in the container."""
  
  pass