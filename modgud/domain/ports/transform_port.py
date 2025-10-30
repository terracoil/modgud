"""Transform service port - high-level contract for AST transformation operations."""

from abc import ABC, abstractmethod
from typing import Any, Callable


class TransformPort(ABC):
  """
  High-level AST transformation service for Surface layer.

  This port defines the contract for transformation operations that
  the surface layer uses. Infrastructure services implement this port.
  """

  @abstractmethod
  def transform_to_implicit_return(
    self,
    func: Callable[..., Any],
    func_name: str,
  ) -> Callable[..., Any]:
    """
    Transform function to use implicit return semantics.

    This is a high-level operation that handles source extraction,
    AST transformation, compilation, and execution in a single call.

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
    pass
