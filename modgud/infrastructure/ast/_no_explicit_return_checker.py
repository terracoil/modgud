"""Find the first explicit return statement anywhere inside a function body."""

import ast


class NoExplicitReturnChecker(ast.NodeVisitor):
  """Find the first explicit ``return`` anywhere inside an implicit-return body.

  Visit each statement of the decorated function's body. The checker descends into
  nested ``def`` / ``async def`` / class bodies too: the whole body is re-compiled
  as one unit, so a ``return`` anywhere in it is refused at decoration time. Lambdas
  need no special case, since they cannot contain a ``return`` statement.
  """

  def __init__(self) -> None:
    """Start with no explicit ``return`` found."""
    self.found: tuple[int, int] | None = None  # (lineno, col) of the first return

  def visit_Return(self, node: ast.Return) -> None:
    """Record the position of the first ``return`` seen; later ones are ignored."""
    if self.found is None:
      self.found = (getattr(node, 'lineno', 0), getattr(node, 'col_offset', 0))
