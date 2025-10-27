"""Port interfaces defining contracts between layers."""

from abc import ABC, abstractmethod
from ast import Module
from typing import Any, Optional, Tuple

from .types import FailureBehavior, GuardFunction


class GuardCheckerPort(ABC):
  """Port for guard validation logic."""

  @abstractmethod
  def check_guards(
    self, guards: Tuple[GuardFunction, ...], args: Tuple[Any, ...], kwargs: dict[str, Any]
  ) -> Optional[str]:
    """Evaluate guards and return error message if any fail."""
    pass

  @abstractmethod
  def handle_failure(
    self,
    error_msg: str,
    on_error: FailureBehavior,
    func_name: str,
    args: Tuple[Any, ...],
    kwargs: dict[str, Any],
    log_enabled: bool,
  ) -> Tuple[Any, Optional[BaseException]]:
    """Handle guard failure according to on_error strategy."""
    pass


class AstTransformerPort(ABC):
  """Port for AST transformation logic."""

  @abstractmethod
  def transform_function_ast(self, fn_node: Any, func_name: str) -> Any:
    """Transform function AST to enforce implicit return semantics."""
    pass

  @abstractmethod
  def apply_implicit_return_transform(self, func_source: str, func_name: str) -> Tuple[Module, str]:
    """Apply implicit return transformation to function source code."""
    pass
