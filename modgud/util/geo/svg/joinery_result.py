"""Result container for Joinery multi-component output."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from modgud.domain.ports import VectorPort

from .svg_converter import SVGConverter


@dataclass(frozen=True)
class JoineryResult:
  """Result container for Joinery multi-component output."""

  left: Sequence[VectorPort]
  right: Sequence[VectorPort]
  teeth: Sequence[VectorPort]

  def to_dict(self) -> dict[str, list[str]]:
    """Convert to legacy dictionary format."""
    return SVGConverter.joinery_dict(self.left, self.right, self.teeth)

  def combined(self) -> Sequence[VectorPort]:
    """Return all components as a single vector sequence."""
    combined_vectors: list[VectorPort] = []
    combined_vectors.extend(self.left)
    combined_vectors.extend(self.right)
    combined_vectors.extend(self.teeth)
    return combined_vectors
