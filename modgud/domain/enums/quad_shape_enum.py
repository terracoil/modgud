"""Quadrilateral shape enumeration for modgud domain layer.

Enumeration for all supported quadrilateral shapes, providing a type-safe
way to specify quadrilateral types.
"""

from enum import StrEnum, auto

from modgud.domain.enums import LookupEnum


class QuadShapeEnum(LookupEnum, StrEnum):
  """Enumeration of supported quadrilateral shape types."""

  RECTANGLE = auto()
  SQUARE = auto()
  PARALLELOGRAM = auto()
  RHOMBUS = auto()
  RIGHTANGLE_TRAPEZOID = auto()
  GENERAL_TRAPEZOID = auto()
  ISOSCELES_TRAPEZOID = auto()
  KITE = auto()

  # Note: Using default behavior from LookupEnum which returns first enum (RECTANGLE)
