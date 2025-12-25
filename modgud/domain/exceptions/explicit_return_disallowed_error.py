"""Raised when an explicit return statement is found in a decorated function."""

from .implicit_return_error import ImplicitReturnError

__all__ = ['ExplicitReturnDisallowedError']


class ExplicitReturnDisallowedError(ImplicitReturnError):
  """Raised when an explicit `return` statement is found in a decorated function."""

  pass
