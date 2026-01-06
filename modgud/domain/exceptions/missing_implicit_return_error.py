"""Raised when block cannot yield a name."""

from .implicit_return_error import ImplicitReturnError

__all__ = ['MissingImplicitReturnError']


class MissingImplicitReturnError(ImplicitReturnError):
  """
  Raised when block cannot yield a name.

  Raised when a block is required to yield a name but does not end with
  a (convertible) final expression or a supported branching structure.
  """

  pass
