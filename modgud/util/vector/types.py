"""Types, interfaces, etc for Vectors"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
@dataclass(frozen=True)
class VectorProtocol(Protocol):
  """Vector interface with name w (for quaternions and transformations)."""

  x: float
  y: float
  z: float
  w: float
  name: str | None


VectorSingularType = dict[str, Any] | VectorProtocol | tuple[float]
VectorInputType = list[VectorSingularType] | VectorSingularType

# Primitive Types for Vectors
VectorTargetType = float | int | bool | str
