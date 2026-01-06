"""Rewrite tail positions to assign to implicit result variable."""

import ast

from ...domain import MissingImplicitReturnError, UnsupportedConstructError


class _TailRewriter:
  """
  Rewrite tail positions to assign to implicit result variable.

  Rewrites *tail positions* (the final statement of a block that determines the
  branch's return name) by replacing a final expression with an assignment to a
  hidden result variable. After transforming the top-level body, we append a single
  `return __implicit_result` to the function.

  Supported tail forms:
    - Expr        -> assign to result
    - If          -> both body and orelse must set result via their own tails
    - Try         -> body and each except must set result; else (if present) also sets it
    - Match       -> each case body must set result via its tail
  """

  def __init__(self, result_name: str) -> None:
    self.result_name = result_name

  def _assign(self, value: ast.expr) -> ast.Assign:
    return ast.Assign(targets=[ast.Name(id=self.result_name, ctx=ast.Store())], value=value)

  def rewrite_tail_stmt(self, stmt: ast.stmt) -> list[ast.stmt]:
    """
    Rewrite tail statement to assign to result variable.

    Return a list of statements that replace the given tail statement,
    ensuring the result variable is set on all runtime paths.
    """
    if isinstance(stmt, ast.Expr):
      return [self._assign(stmt.value)]

    if isinstance(stmt, ast.If):
      if not stmt.orelse:
        raise MissingImplicitReturnError(
          'If without else at tail position must have an else clause.',
          getattr(stmt, 'lineno', None),
          getattr(stmt, 'col_offset', None),
        )
      stmt.body = self.rewrite_block(stmt.body)
      stmt.orelse = self.rewrite_block(stmt.orelse)
      return [stmt]

    if isinstance(stmt, ast.Try):
      # Body must produce a name - normal execution path
      stmt.body = self.rewrite_block(stmt.body)
      # Each except must produce a name - error recovery paths need values too
      for h in stmt.handlers:
        h.body = self.rewrite_block(h.body)
      # Else (if present) runs on success, replaces body's name
      if stmt.orelse:
        stmt.orelse = self.rewrite_block(stmt.orelse)
      # Finally runs regardless but can't affect return name - cleanup only
      return [stmt]

    if isinstance(stmt, ast.Match):
      # All cases must set the result
      for case in stmt.cases:
        if not case.body:
          raise MissingImplicitReturnError(
            'Empty match case body cannot yield a name.',
            getattr(stmt, 'lineno', None),
            getattr(stmt, 'col_offset', None),
          )
        case.body = self.rewrite_block(case.body)
      return [stmt]

    if isinstance(stmt, ast.Pass):
      # Pass yields None - consistent with Python's implicit None return
      return [self._assign(ast.Constant(value=None))]

    if isinstance(stmt, ast.Raise):
      # Initialize result before raise - prevents unbound variable if exception caught higher up
      return [self._assign(ast.Constant(value=None)), stmt]

    raise UnsupportedConstructError(
      f'Unsupported tail construct: {type(stmt).__name__}',
      getattr(stmt, 'lineno', None),
      getattr(stmt, 'col_offset', None),
    )

  def rewrite_block(self, body: list[ast.stmt]) -> list[ast.stmt]:
    if not body:
      # Empty block yields None (mimics Python's implicit return None)
      return [self._assign(ast.Constant(value=None))]
    *init, last = body
    new_last = self.rewrite_tail_stmt(last)
    return [*init, *new_last]
