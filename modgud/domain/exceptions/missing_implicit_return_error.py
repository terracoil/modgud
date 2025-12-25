"""Raised when block cannot yield a value."""

from .implicit_return_error import ImplicitReturnError

__all__ = ['MissingImplicitReturnError']


class MissingImplicitReturnError(ImplicitReturnError):
  """
  Raised when block cannot yield a value.

  Raised when a block is required to yield a value but does not end with
  a (convertible) final expression or a supported branching structure.
  """

  pass
