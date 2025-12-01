from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, Protocol, runtime_checkable


@runtime_checkable
@dataclass(frozen=True)
class VectorProtocol(Protocol):
  """Vector interface with name w (for quaternions and transformations)."""

  x: float
  y: float
  z: float
  w: float
  name: str | None

  ZERO: ClassVar[VectorProtocol]
  IDENTITY: ClassVar[VectorProtocol]
  ATTRS: ClassVar[tuple[str]]

  def format(self, dim=2, precision: int = 4) -> str:
    """Format components of vector to given precision."""

  @classmethod
  def zero(cls, name: str | None = None) -> VectorProtocol:
    """Create zero vector."""
    return cls(0, 0, name=name) if name else cls.ZERO

  @classmethod
  def identity(cls, name: str | None = None) -> VectorProtocol:
    """Create zero vector."""
    return cls(0, 0, name=name) if name else cls.IDENTITY
