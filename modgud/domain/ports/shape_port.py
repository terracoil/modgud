from typing import Protocol, Sequence

from .vector_port import VectorPort


class ShapePort(Protocol):
  def build_shape(self) -> Sequence[VectorPort]:
    """
    Build shape
    """
    pass
