"""Service implementing SourceExtractorPort for source code extraction."""

import ast
import inspect
import textwrap
from typing import Any, Callable


class SourceExtractorService:
  """Service for extracting source code from functions."""

  def extract_source(self, func: Callable) -> str:
    """Extract dedented source code from function.

    :param func: Function to extract source from
    :return: Dedented source code string
    :raises ValueError: If source cannot be extracted
    """
    try:
      source = inspect.getsource(func)
      # Remove any indentation
      return textwrap.dedent(source)
    except (TypeError, OSError) as e:
      raise ValueError(f'Cannot extract source from {func.__name__}: {str(e)}') from e

  def get_function_ast(self, func: Callable) -> Any:
    """Get AST representation of function.

    :param func: Function to parse
    :return: AST node representing the function
    :raises SyntaxError: If source cannot be parsed
    """
    source = self.extract_source(func)
    try:
      tree = ast.parse(source)
      # Extract the function definition node
      for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
          if node.name == func.__name__:
            return node
      raise ValueError(f'Function {func.__name__} not found in parsed AST')
    except SyntaxError as e:
      raise SyntaxError(f'Failed to parse source for {func.__name__}: {str(e)}') from e
