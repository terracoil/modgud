"""Pipeable decorator for the app layer.

Provides the @pipeable decorator that wraps a function in a Pipeable, enabling
functional-style pipelines via the | operator.
"""

from __future__ import annotations

from typing import Any, Callable, TypeVar

from modgud.infrastructure import Pipeable

T = TypeVar('T')


class _Pipeable:
  """Decorator that wraps a function in a Pipeable for | operator chaining.

  Handles both regular functions and built-in types (str, int, float, etc.):

      @pipeable
      def add(x, y):
          return x + y

      result = 5 | add(3) | pipeable(str)  # "8"

  """

  def __call__(self, func: Callable[..., T]) -> Pipeable:
    """Wrap a function (or type) in a Pipeable."""
    if isinstance(func, type):

      def type_converter(x: Any) -> Any:
        return func(x)

      type_converter.__name__ = func.__name__
      type_converter.__doc__ = f'Convert to {func.__name__}'
      result = Pipeable(type_converter)
    else:
      result = Pipeable(func)
    return result


pipeable: _Pipeable = _Pipeable()
