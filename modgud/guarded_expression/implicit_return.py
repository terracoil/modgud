"""Pure AST transformation logic for implicit return functionality.

Extracts the AST rewriting logic from implicit_return into a composable,
testable pure function that transforms function nodes to enforce implicit
return semantics.
"""

from __future__ import annotations

import ast
from typing import List, Optional, Tuple

from .errors import (
  ExplicitReturnDisallowedError,
  MissingImplicitReturnError,
  UnsupportedConstructError,
)


class _NoExplicitReturnChecker(ast.NodeVisitor):

  """Check for explicit return statements in top-level function body.

  Ensures no explicit `return` appears in the *top-level* body of the decorated
  function. We deliberately do NOT descend into nested function/async def/lambda
  bodies so those can use normal Python semantics independently.
  """

  def __init__(self) -> None:
    self.found: Optional[Tuple[int, int]] = None  # (lineno, col)

  def visit_Return(self, node: ast.Return) -> None:  # type: ignore[override]
    # If we are called, it means we're at top-level (we never recurse into nested defs)
    self.found = (getattr(node, 'lineno', 0), getattr(node, 'col_offset', 0))

  # Block traversal into nested defs/lambdas
  def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # type: ignore[override]
    return

  def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # type: ignore[override]
    return

  def visit_Lambda(self, node: ast.Lambda) -> None:  # type: ignore[override]
    return


class _TailRewriter:

  """Rewrite tail positions to assign to implicit result variable.

  Rewrites *tail positions* (the final statement of a block that determines the
  branch's return value) by replacing a final expression with an assignment to a
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

  def rewrite_tail_stmt(self, stmt: ast.stmt) -> List[ast.stmt]:
    """Rewrite tail statement to assign to result variable.

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
      # Body must produce a value
      stmt.body = self.rewrite_block(stmt.body)
      # Each except must produce a value
      for h in stmt.handlers:
        h.body = self.rewrite_block(h.body)
      # Else (if present) also produces a value (it runs on success)
      if stmt.orelse:
        stmt.orelse = self.rewrite_block(stmt.orelse)
      # finally is allowed, but it shouldn't need to assign result; it runs after
      # the above assignments. We leave it unchanged.
      return [stmt]

    if isinstance(stmt, ast.Match):
      # All cases must set the result
      for case in stmt.cases:
        if not case.body:
          raise MissingImplicitReturnError(
            'Empty match case body cannot yield a value.',
            getattr(stmt, 'lineno', None),
            getattr(stmt, 'col_offset', None),
          )
        case.body = self.rewrite_block(case.body)
      return [stmt]

    if isinstance(stmt, ast.Pass):
      raise MissingImplicitReturnError(
        'Pass statement cannot yield a value.',
        getattr(stmt, 'lineno', None),
        getattr(stmt, 'col_offset', None),
      )

    raise UnsupportedConstructError(
      f'Unsupported tail construct: {type(stmt).__name__}',
      getattr(stmt, 'lineno', None),
      getattr(stmt, 'col_offset', None),
    )

  def rewrite_block(self, body: List[ast.stmt]) -> List[ast.stmt]:
    if not body:
      raise MissingImplicitReturnError('Empty block where a value is required.')
    *init, last = body
    new_last = self.rewrite_tail_stmt(last)
    return [*init, *new_last]


class ImplicitReturnTransformer:
  """AST transformation for implicit return functionality."""

  @classmethod
  def transform_function_ast(cls, fn_node: ast.AST, func_name: str) -> ast.AST:
    """Transform function AST to enforce implicit return semantics.

    Transforms a FunctionDef/AsyncFunctionDef AST node to enforce
    implicit return semantics.

    Steps:
      1. Verify no explicit `return` at top-level
      2. Rewrite tail of the function body to assign to a hidden result var
      3. Append a single `return __implicit_result`

    Args:
        fn_node: The function AST node to transform
        func_name: Name of the function (for error messages)

    Returns:
        The transformed AST node with implicit return semantics

    Raises:
        ExplicitReturnDisallowedError: If explicit return found at top level
        MissingImplicitReturnError: If a block cannot yield a value
        UnsupportedConstructError: If an unsupported construct is found

    """
    assert isinstance(fn_node, (ast.FunctionDef, ast.AsyncFunctionDef))
    body = fn_node.body

    # Check for explicit return at top-level
    checker = _NoExplicitReturnChecker()
    # Visit only top-level statements
    for stmt in body:
      checker.visit(stmt)
    if checker.found is not None:
      line, col = checker.found
      raise ExplicitReturnDisallowedError(
        f"Explicit `return` is disallowed in '@guarded_expression' function '{func_name}' with implicit_return=True.",
        line,
        col,
      )

    result_name = '__implicit_result'
    rewriter = _TailRewriter(result_name)
    new_body = rewriter.rewrite_block(body)
    # Append the single return
    new_body.append(ast.Return(value=ast.Name(id=result_name, ctx=ast.Load())))
    fn_node.body = new_body
    return fn_node

  @classmethod
  def apply_implicit_return_transform(
    cls, func_source: str, func_name: str
  ) -> Tuple[ast.Module, str]:
    """Apply implicit return transformation to function source code.

    Args:
        func_source: The source code of the function (dedented)
        func_name: The name of the function to transform

    Returns:
        Tuple of (transformed_ast, compiled_code_object)

    Raises:
        ExplicitReturnDisallowedError: If explicit return found
        MissingImplicitReturnError: If a block cannot yield a value
        UnsupportedConstructError: If an unsupported construct is found

    """
    tree = ast.parse(func_source)
    transformer = _TopLevelTransformer(func_name, cls)
    new_tree = transformer.visit(tree)
    ast.fix_missing_locations(new_tree)
    return new_tree, f'<{func_name}-implicit>'


class _TopLevelTransformer(ast.NodeTransformer):
  """Transform only the target function definition.

  Applies transformation only to the *decorated* function definition that we parsed.
  We rely on inspect.getsource(func) returning just that function (common in modules).
  Strips all decorators to prevent re-application during exec.
  """

  def __init__(self, target_name: str, transformer_cls: type) -> None:
    self.target_name = target_name
    self.transformer_cls = transformer_cls
    super().__init__()

  def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:  # type: ignore[override]
    if node.name == self.target_name:
      node.decorator_list = []
      return self.transformer_cls.transform_function_ast(node, node.name)
    return node

  def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:  # type: ignore[override]
    if node.name == self.target_name:
      node.decorator_list = []
      return self.transformer_cls.transform_function_ast(node, node.name)
    return node
