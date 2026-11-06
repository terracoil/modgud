"""Base exception for implicit-return transformation errors."""

__all__ = ['ImplicitReturnError']


class ImplicitReturnError(SyntaxError):
  """Base class for implicit-return related transformation errors."""

  def __init__(
    self, message: str, lineno: int | None = None, col_offset: int | None = None
  ) -> None:
    """Initialize with optional source location."""
    super().__init__(message)
    if lineno is not None:
      self.lineno = lineno
    if col_offset is not None:
      self.offset = col_offset
