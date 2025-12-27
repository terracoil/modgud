"""Check for explicit return statements in top-level function body."""

import ast


class _NoExplicitReturnChecker(ast.NodeVisitor):
  """
  Check for explicit return statements in top-level function body.

  Ensures no explicit `return` appears in the *top-level* body of the decorated
  function. We deliberately do NOT descend into nested function/async def/lambda
  bodies so those can use normal Python semantics independently.
  """

  def __init__(self) -> None:
    self.found: tuple[int, int] | None = None  # (lineno, col)

  def visit_Return(self, node: ast.Return) -> None:
    # If we are called, it means we're at top-level (we never recurse into nested defs)
    self.found = (getattr(node, 'lineno', 0), getattr(node, 'col_offset', 0))

  # Block traversal into nested defs/lambdas - they retain standard Python semantics
  def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
    return

  def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
    return

  def visit_Lambda(self, node: ast.Lambda) -> None:
    return
