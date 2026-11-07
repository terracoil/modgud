"""Exception raised for an ``eop_`` form in a place it cannot be lowered."""

from .implicit_return_error import ImplicitReturnError

__all__ = ['MarkerPlacementError']


class MarkerPlacementError(ImplicitReturnError):
  """An ``eop_`` form sits where it cannot be lowered, so the function cannot be decorated."""
