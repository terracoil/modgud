"""Implicit-return transformation exceptions.

All errors raised by the implicit-return AST rewrite. `ImplicitReturnError`
is the common base; the three subclasses identify the specific failure mode.
"""

__all__ = [
  'ExplicitReturnDisallowedError',
  'ImplicitReturnError',
  'MissingImplicitReturnError',
  'UnsupportedConstructError',
]


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


class ExplicitReturnDisallowedError(ImplicitReturnError):
  """Raised when an explicit `return` statement is found in an implicit-return function."""


class MissingImplicitReturnError(ImplicitReturnError):
  """Raised when a branch cannot yield a value (no tail expression, empty block, etc.)."""


class UnsupportedConstructError(ImplicitReturnError):
  """Raised when an unsupported AST construct appears at a required return boundary."""
