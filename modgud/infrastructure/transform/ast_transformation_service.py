"""Service implementing ASTTransformationPort for AST manipulation."""

import ast
from typing import Any


class ASTTransformationService:
  """Service for AST manipulation and transformation."""

  def strip_decorators(self, ast_node: Any) -> Any:
    """
    Remove decorators from AST node to prevent re-application.

    :param ast_node: AST node to process
    :return: AST node with decorators removed
    """
    if isinstance(ast_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
      # Create a shallow copy and clear decorators
      ast_node.decorator_list = []
    return ast_node

  def transform_to_implicit_return(self, ast_node: Any) -> Any:
    """
    Transform AST to use implicit returns.

    This delegates to the ImplicitReturnTransformer for the actual transformation.

    :param ast_node: Function AST to transform
    :return: Transformed AST with implicit returns
    :raises ImplicitReturnError: If transformation fails
    """
    # Import here to avoid circular dependency
    from ..implicit_return import ImplicitReturnTransformer

    if not isinstance(ast_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
      raise ValueError('AST node must be a function definition')

    # Use the transformer's method
    return ImplicitReturnTransformer.apply_transform_to_function_node(ast_node)

  def compile_ast(self, ast_node: Any, filename: str, mode: str = 'exec') -> Any:
    """
    Compile AST node to code object.

    :param ast_node: AST to compile
    :param filename: Filename for error messages
    :param mode: Compilation mode
    :return: Compiled code object
    """
    # Ensure the AST is valid
    ast.fix_missing_locations(ast_node)
    return compile(ast_node, filename, mode)
