"""SVG Conversion Utilities for ShapePort migration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from ...domain.ports.vector_port import VectorPort
from .vector_path import VectorPath


@dataclass(frozen=True)
class SVGConverter:
  """Convert vector sequences to SVG paths for backward compatibility."""

  @staticmethod
  def vectors_to_svg(
    vectors: Sequence[VectorPort], close: bool = True, name: str = ''
  ) -> list[str]:
    """
    Convert vector sequence to SVG path commands.

    :param vectors: Sequence of vectors to convert
    :param close: Whether to close the path (default True for shapes)
    :param name: Optional name for the path
    :return: List of SVG command strings
    """
    if not vectors:
      return []

    # Create VectorPath from the vector sequence
    path = VectorPath(close=close, name=name, abs_segments=list(vectors))

    # Generate SVG commands and return as list
    return list(path.svg_path())

  @staticmethod
  def shape_dict(
    vectors: Sequence[VectorPort], key: str = 'shape', close: bool = True, name: str = ''
  ) -> dict[str, list[str]]:
    """
    Create legacy dictionary format from vectors.

    :param vectors: Sequence of vectors to convert
    :param key: Dictionary key for the shape (default 'shape')
    :param close: Whether to close the path
    :param name: Optional name for the path
    :return: Dictionary with single key containing SVG commands
    """
    svg_commands = SVGConverter.vectors_to_svg(vectors, close=close, name=name)
    return {key: svg_commands}

  @staticmethod
  def joinery_dict(
    left: Sequence[VectorPort], right: Sequence[VectorPort], teeth: Sequence[VectorPort]
  ) -> dict[str, list[str]]:
    """
    Convert Joinery components to legacy format.

    :param left: Left component vectors
    :param right: Right component vectors
    :param teeth: Teeth component vectors
    :return: Dictionary with 'left', 'right', 'teeth' keys containing SVG commands
    """
    return {
      'left': SVGConverter.vectors_to_svg(left, close=True, name='left'),
      'right': SVGConverter.vectors_to_svg(right, close=True, name='right'),
      'teeth': SVGConverter.vectors_to_svg(teeth, close=True, name='teeth'),
    }


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


def migrate_shape_result(
  vectors: Sequence[VectorPort], legacy_key: str = 'shape'
) -> dict[str, list[str]]:
  """
  Helper to maintain backward compatibility during migration.

  :param vectors: Vector sequence from new ShapePort.build_shape()
  :param legacy_key: Key to use in legacy dictionary format
  :return: Legacy dictionary format for existing code
  """
  return SVGConverter.shape_dict(vectors, key=legacy_key)
