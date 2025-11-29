"""Vector Implementation."""

from __future__ import annotations

from .types import VectorProtocol
from .vector import Vector

# Make interfaces via generics:
# vector_fields = ['x', 'y', 'z', 'w']
# VectorProtocol=make_dataclass(cls_name="Vector", bases=(Protocol,), fields=[(f,Primitive) for f in vector_fields])
# FloatVectorPort=make_dataclass(cls_name="FloatVector", bases=(VectorProtocol[float],Protocol), fields=[(f,Primitive) for f in vector_fields])


class Vectors:
  ZERO: VectorProtocol = Vector(0.0, 0.0, 0.0, 0.0)
  IDENTITY: VectorProtocol = Vector(1.0, 1.0, 1.0, 1.0)
