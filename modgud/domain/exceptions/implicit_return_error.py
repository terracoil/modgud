"""Base class for implicit-return related transformation errors."""

from typing import Optional

__all__ = ['ImplicitReturnError']


class ImplicitReturnError(SyntaxError):
  """Base class for implicit-return related transformation errors."""

  def __init__(
    self, message: str, lineno: Optional[int] = None, col_offset: Optional[int] = None
  ) -> None:
    """Initialize the ImplicitReturnError with location information.

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
