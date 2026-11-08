"""Exception raised for a malformed ``eop_`` form."""

from .implicit_return_error import ImplicitReturnError

__all__ = ['MarkerUsageError']


class MarkerUsageError(ImplicitReturnError):
  """An ``eop_`` form is malformed, so the function cannot be decorated."""
