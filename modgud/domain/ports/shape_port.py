from typing import Protocol, Sequence, runtime_checkable

from .vector_port import VectorPort


@runtime_checkable
class ShapePort(Protocol):
  def build_shape(self) -> Sequence[VectorPort]:
    """Build shape as specified in constructor and return as sequence of VectorPort objects."""
