"""Transform service implementation - transforms functions using AST transformer adapter."""

import inspect
import textwrap
from typing import Any, Callable, Optional

from modgud.domain.ports.ast_transformer_port import AstTransformerPort
from modgud.infrastructure.ports.transform_service_port import TransformServicePort


class TransformService(TransformServicePort):
  """
  Production transform service implementation.

  This service implements the high-level TransformServicePort interface
  by delegating to an AstTransformerPort implementation (adapter).
  """

  def __init__(self, transformer: Optional[AstTransformerPort] = None):
    """
    Initialize transform service.

    Args:
        transformer: Optional AST transformer adapter. If None, default will be lazy-loaded.

    """
    self._transformer = transformer

  @property
  def transformer(self) -> AstTransformerPort:
    """Lazy-load default AST transformer if not injected."""
    if self._transformer is None:
      from ..adapters.ast_transformer_adapter import AstTransformerAdapter

      self._transformer = AstTransformerAdapter()
    return self._transformer

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

    tree, filename = self.transformer.apply_implicit_return_transform(dedented, func_name)

    code = compile(tree, filename, 'exec')
    namespace: dict[str, Any] = func.__globals__.copy()
    exec(code, namespace)

    result: Callable[..., Any] = namespace[func_name]
    return result
