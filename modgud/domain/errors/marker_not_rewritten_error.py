"""Exception raised when an ``eop_`` form runs as a plain call."""

__all__ = ['MarkerNotRewrittenError']


class MarkerNotRewrittenError(RuntimeError):
  """An ``eop_`` form ran as a plain call because no modgud decorator rewrote it."""

  def __init__(self, name: str) -> None:
    """Name the form and say how to fix the call site."""
    self.name: str = name
    super().__init__(
      f'{name} only works inside a function decorated with @guarded_expression or '
      f'@implicit_return(); the decorator rewrites the call at decoration time.'
    )
