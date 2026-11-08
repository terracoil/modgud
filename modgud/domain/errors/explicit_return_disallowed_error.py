"""Exception raised when an explicit `return` appears in an implicit-return function."""

from .implicit_return_error import ImplicitReturnError

__all__ = ['ExplicitReturnDisallowedError']


class ExplicitReturnDisallowedError(ImplicitReturnError):
  """Raised when an explicit `return` statement is found in an implicit-return function."""
