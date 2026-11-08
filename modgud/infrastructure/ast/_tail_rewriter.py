"""Rewrite tail positions to assign to implicit result variable."""

import ast

from modgud.domain.errors import MissingImplicitReturnError, UnsupportedConstructError


class TailRewriter:
  """Rewrite tail positions to assign to implicit result variable.

  Rewrites *tail positions* (the final statement of a block that determines the
  branch's return name) by replacing a final expression with an assignment to a
  hidden result variable. After transforming the top-level body, we append a single
  `return __implicit_result` to the function.

  Supported tail forms:
    - Expr        -> assign to result
    - If          -> both body and orelse must set result via their own tails
    - Try         -> body and each except must set result; else (if present) also sets it
    - Match       -> each case body must set result via its tail, and the last case
                     must be irrefutable (``case _:`` or a bare capture, no guard)
  """

  def __init__(self, result_name: str) -> None:
    """Remember the hidden variable each tail position assigns to.

    :param result_name: Name of the variable the appended single ``return`` reads.
    """
    self.result_name: str = result_name

  def _assign(self, value: ast.expr) -> ast.Assign:
    return ast.Assign(targets=[ast.Name(id=self.result_name, ctx=ast.Store())], value=value)

  def rewrite_tail_stmt(self, stmt: ast.stmt) -> list[ast.stmt]:
    """Rewrite tail statement to assign to result variable.

    Return a list of statements that replace the given tail statement,
    ensuring the result variable is set on all runtime paths.

    :raises MissingImplicitReturnError: For an ``if`` without ``else`` or a ``match`` without
      a final irrefutable case.
    :raises UnsupportedConstructError: For any other statement kind at tail position.
    """
    rewritten: list[ast.stmt] = [stmt]
    if isinstance(stmt, ast.Expr):
      rewritten = [self._assign(stmt.value)]
    elif isinstance(stmt, ast.If):
      self._rewrite_if(stmt)
    elif isinstance(stmt, ast.Try):
      self._rewrite_try(stmt)
    elif isinstance(stmt, ast.Match):
      self._rewrite_match(stmt)
    elif isinstance(stmt, ast.Pass):
      # Pass yields None - consistent with Python's implicit None return
      rewritten = [self._assign(ast.Constant(value=None))]
    elif isinstance(stmt, ast.Raise):
      # Initialize result before raise - prevents unbound variable if exception caught higher up
      rewritten = [self._assign(ast.Constant(value=None)), stmt]
    else:
      raise UnsupportedConstructError(
        f'Unsupported tail construct: {type(stmt).__name__}',
        getattr(stmt, 'lineno', None),
        getattr(stmt, 'col_offset', None),
      )
    return rewritten

  def _rewrite_if(self, stmt: ast.If) -> None:
    """Rewrite both branches; without ``else`` the fall-through path would yield nothing."""
    if not stmt.orelse:
      raise MissingImplicitReturnError(
        'If without else at tail position must have an else clause.',
        getattr(stmt, 'lineno', None),
        getattr(stmt, 'col_offset', None),
      )
    stmt.body = self.rewrite_block(stmt.body)
    stmt.orelse = self.rewrite_block(stmt.orelse)

  def _rewrite_try(self, stmt: ast.Try) -> None:
    """Rewrite the body, every handler and ``else``; ``finally`` is cleanup and yields nothing."""
    stmt.body = self.rewrite_block(stmt.body)
    for handler in stmt.handlers:
      handler.body = self.rewrite_block(handler.body)
    # Else runs on success and replaces the body's value
    if stmt.orelse:
      stmt.orelse = self.rewrite_block(stmt.orelse)

  def _rewrite_match(self, stmt: ast.Match) -> None:
    """Rewrite every case; the last must be irrefutable so no subject falls through unset."""
    last: ast.match_case = stmt.cases[-1]
    if last.guard is not None or not self._is_irrefutable(last.pattern):
      raise MissingImplicitReturnError(
        'match at tail position must end in a wildcard case (`case _:` or a bare capture '
        'such as `case other:`, with no guard) so every path yields a value.',
        getattr(stmt, 'lineno', None),
        getattr(stmt, 'col_offset', None),
      )
    for case in stmt.cases:
      if not case.body:
        raise MissingImplicitReturnError(
          'Empty match case body cannot yield a name.',
          getattr(stmt, 'lineno', None),
          getattr(stmt, 'col_offset', None),
        )
      case.body = self.rewrite_block(case.body)

  @classmethod
  def _is_irrefutable(cls, pattern: ast.pattern) -> bool:
    """Tell whether ``pattern`` matches every subject.

    True for ``_``, a bare capture, an ``as`` around either, or an or-pattern with one of them.
    """
    irrefutable: bool = False
    if isinstance(pattern, ast.MatchAs):
      irrefutable = pattern.pattern is None or cls._is_irrefutable(pattern.pattern)
    elif isinstance(pattern, ast.MatchOr):
      irrefutable = any(cls._is_irrefutable(alternative) for alternative in pattern.patterns)
    return irrefutable

  def rewrite_block(self, body: list[ast.stmt]) -> list[ast.stmt]:
    """Rewrite the last statement of ``body`` so the block yields its value.

    :param body: Statements of one block (function body, branch, handler or case).
    :returns: The block with its tail rewritten; an empty block yields ``None``.
    """
    if not body:
      # Empty block yields None (mimics Python's implicit return None)
      return [self._assign(ast.Constant(value=None))]
    *init, last = body
    new_last = self.rewrite_tail_stmt(last)
    return [*init, *new_last]
