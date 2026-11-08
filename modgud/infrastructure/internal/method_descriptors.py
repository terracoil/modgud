"""Unwrap and rewrap ``staticmethod`` / ``classmethod`` objects around the decorators."""

from __future__ import annotations

from typing import Any, Callable, TypeAlias, cast

# A string alias: `staticmethod[...]` is only subscriptable at runtime from Python 3.14 on.
DescriptorKind: TypeAlias = 'type[staticmethod[Any, Any]] | type[classmethod[Any, Any, Any]] | None'


class MethodDescriptors:
  """Let modgud's decorators sit either side of ``@staticmethod`` and ``@classmethod``.

  When modgud is the outer decorator it receives the descriptor object, not a function.
  ``unwrap`` hands back the plain function plus the descriptor type, and ``rewrap`` puts
  the finished function back into a descriptor of the same type.
  """

  @staticmethod
  def unwrap(target: Any) -> tuple[Callable[..., Any], DescriptorKind]:
    """Return ``(function, descriptor_type)``; the type is ``None`` for a plain function."""
    is_descriptor: bool = isinstance(target, (staticmethod, classmethod))
    return (target.__func__, type(target)) if is_descriptor else (target, None)

  @staticmethod
  def rewrap(func: Callable[..., Any], kind: DescriptorKind) -> Callable[..., Any]:
    """Wrap ``func`` back into ``kind`` when the original was a descriptor.

    The result is typed as a callable for the decorators' benefit; a ``classmethod`` object
    only becomes callable once the class binds it.
    """
    return cast(Callable[..., Any], func if kind is None else kind(func))
