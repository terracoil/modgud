"""
Transform service implementation - transforms functions for implicit return semantics.

Consolidates TransformAdapter and AstTransformerAdapter into a single service,
eliminating redundant delegation layers while maintaining port contracts.
"""

from __future__ import annotations

import ast
import inspect
import textwrap
from typing import Any, Callable, List, Optional, Tuple

from ...domain.models.errors import (
  ExplicitReturnDisallowedError,
  MissingImplicitReturnError,
)
from ...domain.ports.ast_transformer_port import AstTransformerPort
from ...domain.ports.transform_port import TransformPort


class _NoExplicitReturnChecker(ast.NodeVisitor):
  """
  Check for explicit return statements in top-level function body.

  Ensures no explicit `return` appears in the *top-level* body of the decorated
  function. We deliberately do NOT descend into nested function/async def/lambda
  bodies so those can use normal Python semantics independently.
  """

  def __init__(self) -> None:
    self.found: Optional[Tuple[int, int]] = None  # (lineno, col)

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


class _TailRewriter:
  """
  Rewrite tail positions to assign to implicit result variable.

  This handles the core logic of transforming expressions in tail position
  to assign their value to __implicit_result.
  """

  IMPLICIT_VAR = '__implicit_result'

  def rewrite_tail_stmt(self, stmt: ast.stmt) -> List[ast.stmt]:
    """Rewrite a statement in tail position."""
    if isinstance(stmt, ast.Expr):
      # Standalone expression becomes assignment
      return [self._make_assignment(stmt.value)]
    elif isinstance(stmt, ast.If):
      return [self._rewrite_if(stmt)]
    elif isinstance(stmt, ast.Match):
      return [self._rewrite_match(stmt)]
    elif isinstance(stmt, ast.Try):
      return [self._rewrite_try(stmt)]
    elif isinstance(stmt, ast.With):
      return [self._rewrite_with(stmt)]
    elif isinstance(stmt, ast.For):
      raise MissingImplicitReturnError('For loop cannot produce an implicit return value')
    elif isinstance(stmt, ast.While):
      raise MissingImplicitReturnError('While loop cannot produce an implicit return value')
    else:
      # Non-expression statements (assignments, etc.) in tail position
      return [stmt, self._make_assignment(ast.Constant(value=None))]

  def _make_assignment(self, value: ast.expr) -> ast.stmt:
    """Create assignment to implicit result variable."""
    return ast.Assign(targets=[ast.Name(id=self.IMPLICIT_VAR, ctx=ast.Store())], value=value)

  def _rewrite_if(self, if_node: ast.If) -> ast.If:
    """Rewrite if statement branches."""
    if not if_node.body:
      raise MissingImplicitReturnError('Empty if body cannot produce a value')

    new_body = self.rewrite_tail_block(if_node.body)

    if if_node.orelse:
      new_orelse = self.rewrite_tail_block(if_node.orelse)
    else:
      # Missing else clause - implicit None
      new_orelse = [self._make_assignment(ast.Constant(value=None))]

    return ast.If(test=if_node.test, body=new_body, orelse=new_orelse)

  def _rewrite_match(self, match_node: ast.Match) -> ast.Match:
    """Rewrite match statement cases."""
    new_cases = []
    for case in match_node.cases:
      if not case.body:
        raise MissingImplicitReturnError('Empty match case cannot produce a value')
      new_body = self.rewrite_tail_block(case.body)
      new_cases.append(ast.match_case(pattern=case.pattern, guard=case.guard, body=new_body))
    return ast.Match(subject=match_node.subject, cases=new_cases)

  def _rewrite_try(self, try_node: ast.Try) -> ast.Try:
    """Rewrite try/except/else/finally blocks."""
    # Only rewrite tail positions in try/except/else, not finally
    new_try_body = self.rewrite_tail_block(try_node.body) if try_node.body else []

    new_handlers = []
    for handler in try_node.handlers:
      new_handler_body = self.rewrite_tail_block(handler.body) if handler.body else []
      new_handlers.append(
        ast.ExceptHandler(type=handler.type, name=handler.name, body=new_handler_body)
      )

    new_orelse = self.rewrite_tail_block(try_node.orelse) if try_node.orelse else []

    return ast.Try(
      body=new_try_body,
      handlers=new_handlers,
      orelse=new_orelse,
      finalbody=try_node.finalbody,  # Finally not rewritten
    )

  def _rewrite_with(self, with_node: ast.With | ast.AsyncWith) -> ast.With | ast.AsyncWith:
    """Rewrite with statement body."""
    if not with_node.body:
      raise MissingImplicitReturnError('Empty with body cannot produce a value')

    new_body = self.rewrite_tail_block(with_node.body)

    if isinstance(with_node, ast.AsyncWith):
      return ast.AsyncWith(items=with_node.items, body=new_body)
    return ast.With(items=with_node.items, body=new_body)

  def rewrite_tail_block(self, body: List[ast.stmt]) -> List[ast.stmt]:
    """Rewrite the tail of a statement block."""
    if not body:
      raise MissingImplicitReturnError('Empty block cannot produce a value')

    *init, last = body
    new_last = self.rewrite_tail_stmt(last)
    return [*init, *new_last]


class _FunctionDefTransformer(ast.NodeTransformer):
  """Find and transform target function definition in AST."""

  def __init__(self, target_name: str, transformer_cls: type[TransformService]) -> None:
    self.target_name = target_name
    self.transformer_cls = transformer_cls
    super().__init__()

  def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
    if node.name == self.target_name:
      node.decorator_list = []  # Strip decorators to prevent infinite recursion during exec
      return self.transformer_cls.transform_function_ast(node, node.name)
    return node

  def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> Any:
    if node.name == self.target_name:
      node.decorator_list = []  # Strip decorators to prevent infinite recursion during exec
      return self.transformer_cls.transform_function_ast(node, node.name)
    return node


class TransformService(TransformPort, AstTransformerPort):
  """
  Consolidated transform service implementing both high-level and low-level ports.

  This service directly implements AST transformation for implicit return semantics,
  eliminating the redundant adapter delegation pattern while maintaining
  backward compatibility with both port interfaces.
  """

  def transform_to_implicit_return(
    self,
    func: Callable[..., Any],
    func_name: str,
  ) -> Callable[..., Any]:
    """
    Transform function to use implicit return semantics.

    Handles source extraction, AST transformation, compilation, and execution.

    Args:
        func: Original function to transform
        func_name: Name of the function

    Returns:
        Transformed function with implicit return semantics

    Raises:
        ExplicitReturnDisallowedError: If explicit return found
        MissingImplicitReturnError: If a block cannot yield a value
        UnsupportedConstructError: If unsupported construct found

    """
    source = inspect.getsource(func)
    dedented = textwrap.dedent(source)

    tree, filename = self.apply_implicit_return_transform(dedented, func_name)

    code = compile(tree, filename, 'exec')
    namespace: dict[str, Any] = func.__globals__.copy()
    exec(code, namespace)

    result: Callable[..., Any] = namespace[func_name]
    return result

  @classmethod
  def apply_implicit_return_transform(cls, source: str, func_name: str) -> Tuple[ast.AST, str]:
    """
    Apply implicit return transformation to source code.

    Args:
        source: Python source code containing the function
        func_name: Name of the function to transform

    Returns:
        Tuple of (transformed_ast, filename)

    Raises:
        ExplicitReturnDisallowedError: If explicit return found
        MissingImplicitReturnError: If a block cannot yield a value
        UnsupportedConstructError: If unsupported construct found

    """
    tree = ast.parse(source)
    transformer = _FunctionDefTransformer(func_name, cls)
    new_tree = transformer.visit(tree)
    ast.fix_missing_locations(new_tree)
    return (new_tree, f'<implicit-return-{func_name}>')

  @classmethod
  def transform_function_ast(cls, fn_node: Any, func_name: str) -> Any:
    """
    Transform function AST to enforce implicit return semantics.

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

    # Preserve docstrings - they're metadata, not executable code to transform
    actual_body = body
    docstring_stmt = None
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
      if isinstance(body[0].value.value, str):
        # First statement is a docstring, skip it
        docstring_stmt = body[0]
        actual_body = body[1:]

    # Step 1: Check for explicit returns
    checker = _NoExplicitReturnChecker()
    for stmt in actual_body:
      checker.visit(stmt)
      if checker.found:
        lineno, col = checker.found
        raise ExplicitReturnDisallowedError(
          f'Function {func_name!r} uses implicit_return=True but has '
          f'explicit return at line {lineno}, col {col}'
        )

    # Step 2: Rewrite tail positions
    rewriter = _TailRewriter()
    if actual_body:
      new_body = rewriter.rewrite_tail_block(actual_body)
    else:
      # Only docstring, no actual code - return None
      new_body = [rewriter._make_assignment(ast.Constant(value=None))]

    # Prepend docstring if it existed
    if docstring_stmt:
      new_body.insert(0, docstring_stmt)

    # Step 3: Append return statement
    return_stmt = ast.Return(value=ast.Name(id=_TailRewriter.IMPLICIT_VAR, ctx=ast.Load()))
    new_body.append(return_stmt)

    # Create new function node with transformed body
    if isinstance(fn_node, ast.AsyncFunctionDef):
      return ast.AsyncFunctionDef(
        name=fn_node.name,
        args=fn_node.args,
        body=new_body,
        decorator_list=fn_node.decorator_list,
        returns=fn_node.returns,
        type_comment=fn_node.type_comment,
      )
    else:
      return ast.FunctionDef(
        name=fn_node.name,
        args=fn_node.args,
        body=new_body,
        decorator_list=fn_node.decorator_list,
        returns=fn_node.returns,
        type_comment=fn_node.type_comment,
      )
