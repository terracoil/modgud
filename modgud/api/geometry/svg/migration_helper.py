"""Helper functions to maintain backward compatibility during migration."""

from __future__ import annotations

from typing import Sequence

from ....domain.ports.vector_port import VectorPort
from .svg_converter import SVGConverter


def migrate_shape_result(
  vectors: Sequence[VectorPort], legacy_key: str = 'shape'
) -> dict[str, list[str]]:
  """
  Maintain backward compatibility during migration.

  :param vectors: Vector sequence from new ShapePort.build_shape()
  :param legacy_key: Key to use in legacy dictionary format
  :return: Legacy dictionary format for existing code
  """
  return SVGConverter.shape_dict(vectors, key=legacy_key)
