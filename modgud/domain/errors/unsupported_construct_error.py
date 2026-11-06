"""Exception raised for unsupported AST constructs at a return boundary."""

from .implicit_return_error import ImplicitReturnError

__all__ = ['UnsupportedConstructError']


class UnsupportedConstructError(ImplicitReturnError):
  """Raised when an unsupported AST construct appears at a required return boundary."""
