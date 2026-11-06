"""Exception raised when a branch cannot yield an implicit return value."""

from .implicit_return_error import ImplicitReturnError

__all__ = ['MissingImplicitReturnError']


class MissingImplicitReturnError(ImplicitReturnError):
  """Raised when a branch cannot yield a value (no tail expression, empty block, etc.)."""
