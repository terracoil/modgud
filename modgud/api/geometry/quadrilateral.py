"""Quadrilateral shape generator with configurable parameters."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional, Sequence

from modgud.domain.ports import ShapePort, VectorPort
from .geo_util import GeoUtil


@dataclass(frozen=True)
class Quadrilateral(ShapePort):
  """Configurable quadrilateral shape generator implementing ShapePort protocol."""

  shape_type: str = 'rectangle'
  params: dict[str, float] = field(default_factory=dict)

  def __post_init__(self) -> None:
    """Validate parameters after initialization."""
    self._validate_params()

  def build_shape(self) -> Sequence[VectorPort]:
    """Build configured shape - satisfies ShapePort protocol."""
    shape_method = getattr(self, self.shape_type, None)
    if not shape_method:
      raise ValueError(f'Unknown shape type: {self.shape_type}')

    result = shape_method(**self.params)
    return result

  def _validate_params(self) -> None:
    """Validate shape parameters based on shape type."""
    # Basic parameter validation - can be extended per shape type
    for name, value in self.params.items():
      if isinstance(value, (int, float)) and value <= 0:
        raise ValueError(f'Parameter {name} must be positive, got {value}')

  # ==================== Private Helper Methods ====================

  @staticmethod
  def _validate_dimension(
    value: float, name: str, min_val: float = 0.0, max_val: float = 1.0, exclusive_min: bool = True
  ) -> None:
    """Validate a dimension is within acceptable range. Delegates to GeoUtil."""
    GeoUtil.validate_dimension(value, name, min_val, max_val, exclusive_min)

  @staticmethod
  def _calc_slant_from_angle(h: float, angle: float) -> float:
    """Calculate horizontal slant offset from height and angle. Delegates to GeoUtil."""
    result = GeoUtil.calc_slant_from_angle(h, angle)
    return result

  @staticmethod
  def _calc_slant_from_side(h: float, side: float) -> float:
    """Calculate horizontal slant offset from height and side length. Delegates to GeoUtil."""
    result = GeoUtil.calc_slant_from_side(h, side)
    return result

  @staticmethod
  def _make_points(coords: list[tuple[float, float]]) -> list[VectorPort]:
    """Convert coordinate tuples to VectorPort objects. Delegates to GeoUtil."""
    result = GeoUtil.make_points(coords)
    return result

  def _make_rect_aligned(self, w: float, h: float) -> list[VectorPort]:
    """
    Create axis-aligned rectangle starting at origin.

    :param float w: Width.
    :param float h: Height.
    :returns: List of 4 vertices in counter-clockwise order.
    :rtype: list[VectorPort]
    """
    coords = [
      (0, 0),  # bottom-left
      (w, 0),  # bottom-right
      (w, h),  # top-right
      (0, h),  # top-left
    ]
    return self._make_points(coords)

  def _make_trapezoid_general(
    self, w1: float, w2: float, h: float, side_left: Optional[float] = None
  ) -> list[VectorPort]:
    """
    Create left-aligned trapezoid with optional left side constraint.

    :param float w1: Bottom width.
    :param float w2: Top width.
    :param float h: Height.
    :param float side_left: Left side length (None creates right-aligned).
    :returns: List of 4 vertices in counter-clockwise order.
    :rtype: list[VectorPort]
    :raises ValueError: If side_left < h.
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
    """
    Create parallelogram with given base, height, and horizontal slant.

    :param float w: Base width.
    :param float h: Height.
    :param float slant: Horizontal slant offset.
    :returns: List of 4 vertices in counter-clockwise order.
    :rtype: list[VectorPort]
    """
    coords = [(0, 0), (w, 0), (w + slant, h), (slant, h)]
    return self._make_points(coords)

  # ==================== Public Shape Methods ====================

  def square(self, side: float) -> list[VectorPort]:
    """
    Create a square with all sides equal, all angles 90°.

    :param float side: Side length (0 < side ≤ 1).
    :returns: List of 4 vertices in counter-clockwise order.
    :rtype: list[VectorPort]
    :raises ValueError: If side not in valid range.
    """
    self._validate_dimension(side, 'Side length')
    return self._make_rect_aligned(side, side)

  def rect(self, w: float, h: float) -> list[VectorPort]:
    """
    Create a rectangle with opposite sides equal, all angles 90°.

    :param float w: Width (0 < w ≤ 1).
    :param float h: Height (0 < h ≤ 1).
    :returns: List of 4 vertices in counter-clockwise order.
    :rtype: list[VectorPort]
    :raises ValueError: If w or h not in valid range.
    """
    self._validate_dimension(w, 'Width')
    self._validate_dimension(h, 'Height')
    return self._make_rect_aligned(w, h)

  def parallelogram(
    self, w: float, h: float, angle: Optional[float] = None, side: Optional[float] = None
  ) -> list[VectorPort]:
    """
    Create a parallelogram with opposite sides parallel and equal.

    :param float w: Base width (0 < w ≤ 1).
    :param float h: Perpendicular height (0 < h ≤ 1).
    :param float angle: Slant angle in degrees from horizontal (0 < angle < 180).
        Required if side not provided.
    :param float side: Slanted side length. Required if angle not provided.
    :returns: List of 4 vertices in counter-clockwise order.
    :rtype: list[VectorPort]
    :raises ValueError: If parameters invalid or both/neither angle and side specified.
    """
    self._validate_dimension(w, 'Width')
    self._validate_dimension(h, 'Height')

    if (angle is None) == (side is None):
      raise ValueError('Specify exactly one of: angle or side')

    if angle is not None:
      slant = self._calc_slant_from_angle(h, angle)
    else:
      slant = self._calc_slant_from_side(h, side)

    return self._make_parallelogram_general(w, h, slant)

  def rhombus(
    self, side: float, angle: Optional[float] = None, h: Optional[float] = None
  ) -> list[VectorPort]:
    """
    Create a rhombus with all sides equal length.

    :param float side: Side length (0 < side ≤ 1).
    :param float angle: Base angle in degrees (0 < angle < 180).
        Required if h not provided.
    :param float h: Perpendicular height. Required if angle not provided.
    :returns: List of 4 vertices in counter-clockwise order.
    :rtype: list[VectorPort]
    :raises ValueError: If parameters invalid or both/neither angle and h specified.
    """
    self._validate_dimension(side, 'Side length')

    if (angle is None) == (h is None):
      raise ValueError('Specify exactly one of: angle or h')

    if angle is not None:
      height = side * math.sin(math.radians(angle))
      slant = self._calc_slant_from_angle(height, angle)
    else:
      if h > side:
        raise ValueError(f'Height ({h}) cannot exceed side length ({side})')
      height = h
      slant = self._calc_slant_from_side(height, side)

    return self._make_parallelogram_general(side, height, slant)

  def rightangle_trapezoid(
    self, w1: float, w2: Optional[float] = None, h: float = 1.0
  ) -> list[VectorPort]:
    """
    Create a right-angle trapezoid with left side perpendicular to base.

    :param float w1: Bottom width (0 < w1 ≤ 1).
    :param float w2: Top width (defaults to 1.0).
    :param float h: Height (0 < h ≤ 1).
    :returns: List of 4 vertices in counter-clockwise order.
    :rtype: list[VectorPort]
    :raises ValueError: If parameters not in valid range.
    """
    self._validate_dimension(w1, 'Bottom width')
    self._validate_dimension(h, 'Height')

    w2 = w2 or 1.0
    self._validate_dimension(w2, 'Top width')

    return self._make_trapezoid_general(w1, w2, h, side_left=h)

  def general_trapezoid(
    self, w1: float, w2: Optional[float] = None, h: float = 1.0, side_left: Optional[float] = None
  ) -> list[VectorPort]:
    """
    Create a general trapezoid with one pair of parallel sides.

    :param float w1: Bottom width (0 < w1 ≤ 1).
    :param float w2: Top width (defaults to 1.0).
    :param float h: Height (0 < h ≤ 1).
    :param float side_left: Left side length (optional, creates right-aligned if None).
    :returns: List of 4 vertices in counter-clockwise order.
    :rtype: list[VectorPort]
    :raises ValueError: If parameters not in valid range.
    """
    self._validate_dimension(w1, 'Bottom width')
    self._validate_dimension(h, 'Height')

    w2 = w2 or 1.0
    self._validate_dimension(w2, 'Top width')

    return self._make_trapezoid_general(w1, w2, h, side_left)

  def isosceles_trapezoid(
    self, w1: float, w2: Optional[float] = None, h: float = 1.0, side: Optional[float] = None
  ) -> list[VectorPort]:
    """
    Create an isosceles trapezoid with equal non-parallel sides.

    :param float w1: Bottom width (0 < w1 ≤ 1).
    :param float w2: Top width (defaults to 1.0).
    :param float h: Height (0 < h ≤ 1).
    :param float side: Slanted side length (auto-calculated if None).
    :returns: List of 4 vertices in counter-clockwise order.
    :rtype: list[VectorPort]
    :raises ValueError: If parameters invalid or geometrically inconsistent.
    """
    self._validate_dimension(w1, 'Bottom width')
    self._validate_dimension(h, 'Height')

    w2 = w2 or 1.0
    self._validate_dimension(w2, 'Top width')

    width_diff = abs(w1 - w2)
    half_diff = width_diff / 2.0
    calculated_side = math.sqrt(h**2 + half_diff**2)

    if side is not None:
      if abs(side - calculated_side) > 1e-6:
        raise ValueError(
          f'Specified side ({side}) inconsistent with geometry. '
          f'For w1={w1}, w2={w2}, h={h}, side must be ~{calculated_side:.6f}'
        )
      side_left = side
    else:
      side_left = calculated_side

    return self._make_trapezoid_general(w1, w2, h, side_left)

  def kite(self, w: float, h1: float, h2: Optional[float] = None) -> list[VectorPort]:
    """
    Create a kite with two pairs of adjacent equal sides.

    :param float w: Width at widest point (0 < w ≤ 1).
    :param float h1: Top triangle height (0 < h1 ≤ 1).
    :param float h2: Bottom triangle height (defaults to 1.0 - h1).
    :returns: List of 4 vertices in counter-clockwise order.
    :rtype: list[VectorPort]
    :raises ValueError: If parameters invalid or heights exceed unit grid.
    """
    self._validate_dimension(w, 'Width')
    self._validate_dimension(h1, 'Top height')

    h2 = h2 if h2 is not None else (1.0 - h1)
    self._validate_dimension(h2, 'Bottom height')

    if h1 + h2 > 1.0:
      raise ValueError(f'Sum of heights ({h1 + h2}) exceeds 1.0')

    center_x = w / 2.0
    coords = [(center_x, 0), (w, h2), (center_x, h2 + h1), (0, h2)]
    return self._make_points(coords)
