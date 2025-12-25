"""Port definitions for AST transformation and source extraction functionality."""

from typing import Any, Callable, Optional, Protocol, TypeVar, runtime_checkable

T = TypeVar('T')


@runtime_checkable
class ImplicitReturnTransformerPort(Protocol):
  """Port for implicit return transformation functionality."""

  def transform_function(self, func: Callable[..., T]) -> Callable[..., T]:
    """
    Transform function to use implicit returns.

    :param func: Function to transform
    :return: Transformed function with implicit returns
    :raises ImplicitReturnError: If transformation fails
    """
    ...

  def validate_source(self, func: Callable) -> bool:
    """
    Check if function source is available for transformation.

    :param func: Function to validate
    :return: True if source can be extracted and transformed
    """
    ...


@runtime_checkable
class SourceExtractorPort(Protocol):
  """Port for source code extraction functionality."""

  def extract_source(self, func: Callable) -> str:
    """
    Extract dedented source code from function.

    :param func: Function to extract source from
    :return: Dedented source code string
    :raises ValueError: If source cannot be extracted
    """
    ...

  def get_function_ast(self, func: Callable) -> Any:
    """
    Get AST representation of function.

    :param func: Function to parse
    :return: AST node representing the function
    :raises SyntaxError: If source cannot be parsed
    """
    ...


@runtime_checkable
class ASTTransformationPort(Protocol):
  """Port for AST manipulation and transformation."""

  def strip_decorators(self, ast_node: Any) -> Any:
    """
    Remove decorators from AST node to prevent re-application.

    :param ast_node: AST node to process
    :return: AST node with decorators removed
    """
    ...

  def transform_to_implicit_return(self, ast_node: Any) -> Any:
    """
    Transform AST to use implicit returns.

    :param ast_node: Function AST to transform
    :return: Transformed AST with implicit returns
    :raises ImplicitReturnError: If transformation fails
    """
    ...

  def compile_ast(self, ast_node: Any, filename: str, mode: str = 'exec') -> Any:
    """
    Compile AST node to code object.

    :param ast_node: AST to compile
    :param filename: Filename for error messages
    :param mode: Compilation mode
    :return: Compiled code object
    """
    ...


@runtime_checkable
class TransformationResultPort(Protocol):
  """Port for transformation result handling."""

  def create_success(self, func: Callable[..., T]) -> 'TransformationResultPort':
    """Create successful transformation result."""
    ...

  def create_failure(self, error: Exception) -> 'TransformationResultPort':
    """Create failed transformation result."""
    ...

  @property
  def is_success(self) -> bool:
    """Check if transformation succeeded."""
    ...

  @property
  def function(self) -> Optional[Callable]:
    """Get transformed function if successful."""
    ...

  @property
  def error(self) -> Optional[Exception]:
    """Get error if transformation failed."""
    ...
