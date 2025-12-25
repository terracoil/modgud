"""Adapter implementing ImplicitReturnTransformerPort using existing transformer."""

import inspect
from typing import Callable, TypeVar

from ..implicit_return import ImplicitReturnTransformer

T = TypeVar('T')


class ImplicitReturnAdapter:
  """Adapter that implements ImplicitReturnTransformerPort."""

  def __init__(self) -> None:
    """Initialize the adapter."""
    self._transformer = ImplicitReturnTransformer

  def transform_function(self, func: Callable[..., T]) -> Callable[..., T]:
    """
    Transform function to use implicit returns.

    :param func: Function to transform
    :return: Transformed function with implicit returns
    :raises ImplicitReturnError: If transformation fails
    """
    # Get source code
    try:
      source = inspect.getsource(func)
    except (TypeError, OSError) as e:
      raise ValueError(f'Cannot extract source from {func.__name__}: {str(e)}')

    # Remove indentation
    import textwrap

    dedented_source = textwrap.dedent(source)

    # Apply transformation
    transformed_ast, _ = self._transformer.apply_implicit_return_transform(
      dedented_source, func.__name__
    )

    # Compile and execute in function's original namespace
    code = compile(transformed_ast, f'<implicit_return:{func.__name__}>', 'exec')
    namespace = func.__globals__.copy()
    exec(code, namespace)

    # Get the transformed function
    transformed_func = namespace[func.__name__]

    # Preserve metadata
    transformed_func.__name__ = func.__name__
    transformed_func.__doc__ = func.__doc__
    transformed_func.__dict__.update(func.__dict__)
    transformed_func.__annotations__ = func.__annotations__

    return transformed_func

  def validate_source(self, func: Callable) -> bool:
    """
    Check if function source is available for transformation.

    :param func: Function to validate
    :return: True if source can be extracted and transformed
    """
    try:
      source = inspect.getsource(func)
      # Also check if it's not a built-in or C function
      return source is not None and not inspect.isbuiltin(func)
    except (TypeError, OSError):
      return False
