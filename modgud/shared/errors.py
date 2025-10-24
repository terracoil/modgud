"""Shared error classes for the modgud library."""

from typing import Optional


class GuardClauseError(Exception):

  """Exception raised when a guard clause fails."""

  pass


class ImplicitReturnError(SyntaxError):

  """Base class for implicit-return related transformation errors."""

  def __init__(
    self, message: str, lineno: Optional[int] = None, col_offset: Optional[int] = None
  ) -> None:
    """Initialize the ImplicitReturnError with location information.

    Args:
        message: Error message describing the issue
        lineno: Line number where the error occurred
        col_offset: Column offset where the error occurred

    """
    super().__init__(message)
    if lineno is not None:
      self.lineno = lineno  # type: ignore[attr-defined]
    if col_offset is not None:
      self.offset = col_offset  # type: ignore[attr-defined]


class ExplicitReturnDisallowedError(ImplicitReturnError):

  """Raised when an explicit `return` statement is found in a decorated function."""


class MissingImplicitReturnError(ImplicitReturnError):

  """Raised when block cannot yield a value.

  Raised when a block is required to yield a value but does not end with
  a (convertible) final expression or a supported branching structure.
  """


class UnsupportedConstructError(ImplicitReturnError):

  """Raised when an unsupported AST construct appears at a required return boundary."""
