"""Port definition for AST manipulation and transformation."""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ASTTransformationPort(Protocol):
  """Port for AST manipulation and transformation."""

  def strip_decorators(self, ast_node: Any) -> Any:
    """Remove decorators from AST node to prevent re-application.

    :param ast_node: AST node to process
    :return: AST node with decorators removed
    """
    ...

  def transform_to_implicit_return(self, ast_node: Any) -> Any:
    """Transform AST to use implicit returns.

    :param ast_node: Function AST to transform
    :return: Transformed AST with implicit returns
    :raises ImplicitReturnError: If transformation fails
    """
    ...

  def compile_ast(self, ast_node: Any, filename: str, mode: str = 'exec') -> Any:
    """Compile AST node to code object.

    :param ast_node: AST to compile
    :param filename: Filename for error messages
    :param mode: Compilation mode
    :return: Compiled code object
    """
    ...
