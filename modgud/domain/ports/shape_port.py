"""Port definition for shape builders."""

from typing import Protocol, Sequence, runtime_checkable

from .vector_port import VectorPort


@runtime_checkable
class ShapePort(Protocol):
  """Interface for shape builders that return vector sequences."""

  def build_shape(self) -> Sequence[VectorPort]:
    """Build shape as specified in constructor and return as sequence of VectorPort objects."""
