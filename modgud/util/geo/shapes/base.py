"""Base class for all shape implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Sequence

from modgud.domain.ports import ShapePort, VectorPort
from modgud.util.geo import GeoUtil

if TYPE_CHECKING:
  pass


class ShapeBase(ShapePort, ABC):
  """Abstract base class for all shape implementations.

  Provides common functionality and defines the interface that all shapes must implement.
  Each shape must be able to build its vertices and provide edge angle information for
  proper notch alignment.
  """

  @abstractmethod
  def build_shape(self) -> Sequence[VectorPort]:
    """Build the shape vertices with any decorations applied.

    Returns:
      Sequence of VectorPort objects defining the shape boundary

    """
    pass

  @abstractmethod
  def get_edge_angle(self, edge_index: int) -> float:
    """Get the angle of a specific edge for notch calculations.

    Args:
      edge_index: Index of the edge (0=bottom, 1=right, 2=top, 3=left)

    Returns:
      Angle in radians from horizontal for the specified edge

    Note:
      This is critical for proper trapezoid notch alignment where notches
      should follow the angle of the trapezoid's slanted sides.

    """
    pass

  @abstractmethod
  def _build_base_shape(self) -> list[VectorPort]:
    """Build the base shape vertices without decorations.

    Returns:
      List of VectorPort objects defining the basic shape

    """
    pass

  # ==================== Shared Utility Methods ====================

  @staticmethod
  def _calc_slant_from_angle(h: float, angle_rad: float) -> float:
    """Calculate horizontal slant offset from height and angle."""
    result = GeoUtil.calc_slant_from_angle(h, angle_rad)
    return result

  @staticmethod
  def _calc_slant_from_side(h: float, side: float) -> float:
    """Calculate horizontal slant offset from height and side length."""
    result = GeoUtil.calc_slant_from_side(h, side)
    return result

  @staticmethod
  def _make_points(coords: list[tuple[float, float]]) -> list[VectorPort]:
    """Convert coordinate tuples to VectorPort objects."""
    result = GeoUtil.make_points(coords)
    return result

  def _make_rect_aligned(self, w: float, h: float) -> list[VectorPort]:
    """Create axis-aligned rectangle starting at origin.

    Args:
      w: Width
      h: Height

    Returns:
      List of 4 vertices in counter-clockwise order

    """
    coords = [
      (0, 0),  # bottom-left
      (w, 0),  # bottom-right
      (w, h),  # top-right
      (0, h),  # top-left
    ]
    return self._make_points(coords)

  def _make_trapezoid_general(
    self, w1: float, w2: float, h: float, side_left: float | None = None
  ) -> list[VectorPort]:
    """Create general trapezoid with optional left side constraint.

    Args:
      w1: Bottom width
      w2: Top width
      h: Height
      side_left: Optional left side length constraint

    Returns:
      List of 4 vertices in counter-clockwise order

    Raises:
      ValueError: If side_left < h

    """
    if side_left is None:
      left_slant = 0
    else:
      if side_left < h:
        raise ValueError(f'Left side length ({side_left}) must be >= height ({h})')
      left_slant = self._calc_slant_from_side(h, side_left)

    right_slant = left_slant + w1 - w2

    coords = [(0, 0), (w1, 0), (right_slant + w2, h), (left_slant, h)]
    return self._make_points(coords)

  def _make_parallelogram_general(self, w: float, h: float, slant: float) -> list[VectorPort]:
    """Create parallelogram with given base, height, and horizontal slant.

    Args:
      w: Base width
      h: Height
      slant: Horizontal slant offset

    Returns:
      List of 4 vertices in counter-clockwise order

    """
    coords = [(0, 0), (w, 0), (w + slant, h), (slant, h)]
    return self._make_points(coords)

  def _validate_dimension(
    self, value: float, name: str, min_val: float = 0.0, max_val: float = 1.0
  ) -> None:
    """Validate a dimension parameter is within acceptable range.

    Args:
      value: The value to validate
      name: Name of the parameter for error messages
      min_val: Minimum acceptable value (exclusive)
      max_val: Maximum acceptable value (inclusive)

    Raises:
      ValueError: If value is outside acceptable range

    """
    if not (min_val < value <= max_val):
      raise ValueError(f'{name} must be in range ({min_val}, {max_val}], got {value}')
