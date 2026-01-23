"""Transform only the target function definition."""

import ast
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from .implicit_return_transformer import ImplicitReturnTransformer


class _TopLevelTransformer(ast.NodeTransformer):
  """Transform only the target function definition.

  Applies transformation only to the *decorated* function definition that we parsed.
  We rely on inspect.getsource(func) returning just that function (common in modules).
  Strips all decorators to prevent re-application during exec.
  """

  def __init__(self, target_name: str, transformer_cls: type['ImplicitReturnTransformer']) -> None:
    self.target_name = target_name
    self.transformer_cls = transformer_cls
    super().__init__()

  def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
    if node.name == self.target_name:
      node.decorator_list = []  # Strip decorators to prevent infinite recursion during exec
      return self.transformer_cls.transform_function_ast(node, node.name)
    return node

  def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
    if node.name == self.target_name:
      node.decorator_list = []  # Strip decorators to prevent infinite recursion during exec
      return self.transformer_cls.transform_function_ast(node, node.name)
    return node
