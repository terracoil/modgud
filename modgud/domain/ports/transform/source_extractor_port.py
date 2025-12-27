"""Port definition for source code extraction functionality."""

from typing import Any, Callable, Protocol, runtime_checkable


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
