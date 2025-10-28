"""AST transformer port - contract for AST transformation implementations."""

from abc import ABC, abstractmethod
from ast import Module
from typing import Any, Tuple


class AstTransformerPort(ABC):
  """
  Port for AST transformation logic.

  This port defines the contract that infrastructure adapters must implement
  to provide AST transformation capabilities for implicit return semantics.
  """

  @abstractmethod
  def transform_function_ast(self, fn_node: Any, func_name: str) -> Any:
    """
    Transform function AST to enforce implicit return semantics.

    Args:
        fn_node: The function AST node (FunctionDef or AsyncFunctionDef)
        func_name: Name of the function being transformed

    Returns:
        Transformed AST node with implicit return semantics

    Raises:
        ExplicitReturnDisallowedError: If explicit return found
        MissingImplicitReturnError: If a block cannot yield a value
        UnsupportedConstructError: If unsupported construct at tail position

    """
    pass

  @abstractmethod
  def apply_implicit_return_transform(self, func_source: str, func_name: str) -> Tuple[Module, str]:
    """
    Apply implicit return transformation to function source code.

    Args:
        func_source: The source code of the function (dedented)
        func_name: The name of the function to transform

    Returns:
        Tuple of (transformed_ast_module, filename)

    Raises:
        ExplicitReturnDisallowedError: If explicit return found
        MissingImplicitReturnError: If a block cannot yield a value
        UnsupportedConstructError: If unsupported construct found

    """
    pass
