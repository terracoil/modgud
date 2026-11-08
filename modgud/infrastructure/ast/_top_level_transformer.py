"""Transform only the target function definition."""

import ast
from typing import Callable


class TopLevelTransformer(ast.NodeTransformer):
  """Transform only the target function definition.

  Applies transformation only to the *decorated* function definition that we parsed.
  We rely on inspect.getsource(func) returning just that function (common in modules).
  Strips all decorators to prevent re-application during exec.
  """

  def __init__(
    self, target_name: str, transform_function_ast: Callable[[ast.AST, str], ast.AST]
  ) -> None:
    """Capture the function to rewrite and the rewrite to apply.

    :param target_name: Name of the decorated function; other definitions are left alone.
    :param transform_function_ast: Rewrite for the target's definition node. Passed in as a
      callable so this helper does not depend on the transformer adapter.
    """
    self.target_name: str = target_name
    self.transform_function_ast: Callable[[ast.AST, str], ast.AST] = transform_function_ast
    super().__init__()

  def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
    """Rewrite ``node`` if it is the target function."""
    return self._transform_if_target(node)

  def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
    """Rewrite ``node`` if it is the target coroutine function."""
    return self._transform_if_target(node)

  def _transform_if_target(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> ast.AST:
    """Rewrite ``node`` when it is the target definition; return any other node unchanged.

    The target's decorators are stripped so exec'ing the rewritten source cannot re-apply them.
    """
    is_target: bool = node.name == self.target_name
    if is_target:
      node.decorator_list = []
    return self.transform_function_ast(node, node.name) if is_target else node
