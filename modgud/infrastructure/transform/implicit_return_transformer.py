"""AST transformation for implicit return functionality."""

from __future__ import annotations

import ast
import inspect
import textwrap
from typing import Any, Callable, TypeVar

from modgud.domain import ExplicitReturnDisallowedError

T = TypeVar('T')


class ImplicitReturnTransformer:
  """AST transformation for implicit return functionality."""

  @classmethod
  def transform_function(cls, func: Callable[..., T]) -> Callable[..., T]:
    """Transform a function to use implicit returns.

    Extracts source, applies the implicit-return AST rewrite, recompiles
    in the function's original global namespace, and preserves metadata.

    Args:
        func: Function to transform

    Returns:
        Transformed function with implicit return semantics

    Raises:
        ValueError: If source cannot be extracted
        ImplicitReturnError: If transformation fails

    """
    try:
      source = inspect.getsource(func)
    except (TypeError, OSError) as e:
      raise ValueError(f'Cannot extract source from {func.__name__}: {str(e)}') from e

    dedented_source = textwrap.dedent(source)
    transformed_ast, _ = cls.apply_implicit_return_transform(dedented_source, func.__name__)
    code = compile(transformed_ast, f'<implicit_return:{func.__name__}>', 'exec')
    namespace: dict[str, Any] = func.__globals__.copy()
    exec(code, namespace)
    transformed_func: Callable[..., T] = namespace[func.__name__]
    transformed_func.__name__ = func.__name__
    transformed_func.__doc__ = func.__doc__
    transformed_func.__dict__.update(func.__dict__)
    transformed_func.__annotations__ = func.__annotations__
    return transformed_func

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
        MissingImplicitReturnError: If a block cannot yield a name
        UnsupportedConstructError: If an unsupported construct is found

    """
    from ._no_explicit_return_checker import _NoExplicitReturnChecker
    from ._tail_rewriter import _TailRewriter

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

    # Preserve docstrings - they're metadata, not executable code to transform
    actual_body = body
    docstring_stmt = None
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
      if isinstance(body[0].value.value, str):
        # First statement is a docstring, skip it
        docstring_stmt = body[0]
        actual_body = body[1:]

    # Transform the actual body (excluding docstring)
    if actual_body:
      new_body = rewriter.rewrite_block(actual_body)
    else:
      # Only docstring, no actual code - return None
      new_body = [
        ast.Assign(
          targets=[ast.Name(id=result_name, ctx=ast.Store())], value=ast.Constant(value=None)
        )
      ]

    # Prepend docstring if it existed
    if docstring_stmt:
      new_body.insert(0, docstring_stmt)

    # Append the single return
    new_body.append(ast.Return(value=ast.Name(id=result_name, ctx=ast.Load())))
    fn_node.body = new_body
    return fn_node

  @classmethod
  def apply_implicit_return_transform(
    cls, func_source: str, func_name: str
  ) -> tuple[ast.Module, str]:
    """Apply implicit return transformation to function source code.

    Args:
        func_source: The source code of the function (dedented)
        func_name: The name of the function to transform

    Returns:
        Tuple of (transformed_ast, compiled_code_object)

    Raises:
        ExplicitReturnDisallowedError: If explicit return found
        MissingImplicitReturnError: If a block cannot yield a name
        UnsupportedConstructError: If an unsupported construct is found

    """
    from ._top_level_transformer import _TopLevelTransformer

    tree = ast.parse(func_source)
    transformer = _TopLevelTransformer(func_name, cls)
    new_tree = transformer.visit(tree)
    ast.fix_missing_locations(new_tree)
    return new_tree, f'<{func_name}-implicit>'
