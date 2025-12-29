"""Quadrilateral shape generator with configurable parameters."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, Sequence

from modgud.domain.enums import PlacementEnum, QuadShapeEnum
from modgud.domain.ports import ShapePort, VectorPort

from .geo_util import GeoUtil

if TYPE_CHECKING:
  from modgud.domain.ports.noise_port import NoisePort


@dataclass(frozen=True)
class Quadrilateral(ShapePort):
  """Configurable quadrilateral shape generator implementing ShapePort protocol."""

  quad_shape: QuadShapeEnum = QuadShapeEnum.RECTANGLE
  params: dict[str, float] = field(default_factory=dict)
  # Torn edge parameters
  noise: Optional['NoisePort'] = None
  noise_segments: int = 100
  noise_amplitude: float = 5.0
  notch_sides: list[PlacementEnum] = field(default_factory=lambda: [PlacementEnum.NONE])
  notch_depth: float = 0.0
  notch_offset: float = 0.0
  notch_size: float = 0.1
  smoothing_factor: float = 0.1
  torn_sides: list[PlacementEnum] = field(default_factory=lambda: [PlacementEnum.NONE])

  def __post_init__(self) -> None:
    """Validate parameters after initialization."""
    self._validate_params()

  def build_shape(self) -> Sequence[VectorPort]:
    """Build configured shape - satisfies ShapePort protocol."""
    # First build the base shape using convention: enum name lowercased
    # Special case: RECTANGLE maps to 'rect' method
    if self.quad_shape == QuadShapeEnum.RECTANGLE:
      method_name = 'rect'
    else:
      method_name = self.quad_shape.lower()

    shape_method = getattr(self, method_name, None)
    if not shape_method:
      raise ValueError(f'Unknown shape type: {self.quad_shape}')

    base_vertices = shape_method(**self.params)

    # Apply torn edges if specified (check if not just NONE)
    if (
      self.torn_sides and any(side != PlacementEnum.NONE for side in self.torn_sides) and self.noise
    ):
      result = self._apply_torn_edges(base_vertices)
      return result

    return base_vertices

  def _validate_params(self) -> None:
    """Validate shape parameters based on shape type."""
    # Basic parameter validation - can be extended per shape type
    for name, value in self.params.items():
      if isinstance(value, (int, float)) and value <= 0:
        raise ValueError(f'Parameter {name} must be positive, got {value}')

    # Validate torn sides if specified
    if self.torn_sides and any(side != PlacementEnum.NONE for side in self.torn_sides):
      self._validate_torn_sides_enum(self.torn_sides)
      if not self.noise:
        raise ValueError('noise parameter required when torn_sides is specified')

    # Validate noise parameters
    if self.noise_segments < 10 or self.noise_segments > 1000:
      raise ValueError('noise_segments must be between 10 and 1000')

    if self.noise_amplitude < 0.1 or self.noise_amplitude > 50.0:
      raise ValueError('noise_amplitude must be between 0.1 and 50.0')

    if not (0.0 <= self.smoothing_factor <= 1.0):
      raise ValueError('smoothing_factor must be between 0.0 and 1.0')

  def _validate_torn_sides_enum(self, torn_sides: list[PlacementEnum]) -> None:
    """
    Validate torn_sides list contains only valid placement values.

    :param torn_sides: List of PlacementEnum values
    :raises ValueError: If torn_sides contains invalid values
    """
    valid_sides = {
      PlacementEnum.NORTH,
      PlacementEnum.SOUTH,
      PlacementEnum.EAST,
      PlacementEnum.WEST,
      PlacementEnum.NONE,
    }
    for side in torn_sides:
      if side not in valid_sides:
        raise ValueError(
          f'Invalid torn side: {side}. Must be one of: NORTH, SOUTH, EAST, WEST, or NONE'
        )

  def _apply_torn_edges(self, vertices: list[VectorPort]) -> list[VectorPort]:
    """Apply torn edges to the quadrilateral shape."""
    if len(vertices) != 4:
      raise ValueError('Torn edges only supported for quadrilaterals (4 vertices)')

    # Convert torn_sides list to set for efficient lookup
    torn_sides_set = set(self.torn_sides)

    # Define edges in clockwise order to match TornPaper convention
    # Quadrilateral vertices are typically: bottom-left, bottom-right, top-right, top-left
    edges = [
      (PlacementEnum.NORTH, vertices[3], vertices[2], 'top'),  # North: top-left to top-right
      (PlacementEnum.EAST, vertices[1], vertices[2], 'right'),  # East: bottom-right to top-right
      (
        PlacementEnum.SOUTH,
        vertices[0],
        vertices[1],
        'bottom',
      ),  # South: bottom-left to bottom-right
      (PlacementEnum.WEST, vertices[0], vertices[3], 'left'),  # West: bottom-left to top-left
    ]

    # Collect all points for the final shape
    all_points = []

    for side_enum, start_point, end_point, _edge_name in edges:
      if side_enum in torn_sides_set:
        # Create torn edge with adjusted amplitude
        # Convert enum to string for GeoUtil compatibility
        side_str = side_enum.name[0]  # Get first letter (N, S, E, W)
        adjusted_amplitude = GeoUtil.get_fitting_amplitude(self.noise_amplitude, side_str)
        scaled_noise = GeoUtil.create_scaled_noise(self.noise, adjusted_amplitude)

        # Create torn edge points (excluding start to avoid duplication)
        edge_points = GeoUtil.create_torn_edge(
          start_point, end_point, scaled_noise, self.noise_segments, self.smoothing_factor
        )
        all_points.extend(edge_points[1:])  # Skip first point to avoid duplication
      else:
        # Straight edge - just add the end point
        all_points.append(end_point)

    return all_points

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
