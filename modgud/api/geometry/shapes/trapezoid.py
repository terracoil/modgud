"""Trapezoid shape with two parallel sides and auto-variant detection."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, Sequence

from modgud.domain.enums import OrdinalEnum, TrapezoidEnum
from modgud.domain.ports import VectorPort

from .base import ShapeBase
from .mixins import NotchesMixin, TornEdgesMixin, ValidationMixin

if TYPE_CHECKING:
  from modgud.domain.ports.noise_port import NoisePort


@dataclass(frozen=True)
class Trapezoid(ShapeBase, ValidationMixin, TornEdgesMixin, NotchesMixin):
  """
  Trapezoid shape with two parallel sides and automatic variant detection.

  A trapezoid has one pair of parallel sides (bases). The variant is automatically
  determined from the parameters:
  - GENERAL: Generic trapezoid with any angles
  - RIGHT_ANGLE: Left side forms 90° angle (side_left == height)
  - ISOSCELES: Symmetric trapezoid (equal angles on both sides)

  Key feature: get_edge_angle() provides correct angles for proper notch alignment,
  fixing the issue where notches were always perpendicular instead of following
  the trapezoid's slanted edges.
  """

  # Required geometric parameters
  w1: float  # Bottom width (base)
  w2: float  # Top width (top)
  h: float  # Height
  side_left: Optional[float] = None  # Optional left side constraint

  # Decorative parameters
  torn_sides: list[OrdinalEnum] = field(default_factory=lambda: [OrdinalEnum.NONE])
  notch_sides: list[OrdinalEnum] = field(default_factory=lambda: [OrdinalEnum.NONE])

  # Torn edge parameters
  noise: Optional['NoisePort'] = None
  noise_amplitude: float = 5.0
  noise_segments: int = 100
  smoothing_factor: float = 0.1

  # Notch parameters
  notch_depth: float = 0.0
  notch_offset: float = 0.0
  notch_size: float = 0.1

  # Auto-calculated variant (set in __post_init__)
  variant: TrapezoidEnum = field(init=False)

  def __post_init__(self) -> None:
    """Validate parameters and determine trapezoid variant."""
    # Auto-calculate variant from parameters
    object.__setattr__(
      self, 'variant', TrapezoidEnum.from_params(self.w1, self.w2, self.h, self.side_left)
    )

    # Validate all parameters
    self._validate_params()

  def build_shape(self) -> Sequence[VectorPort]:
    """
    Build trapezoid shape with optional decorations.

    Returns:
      Sequence of VectorPort objects defining the trapezoid boundary

    """
    # Start with base trapezoid
    vertices = self._build_base_shape()

    # Apply decorations
    vertices = self._apply_decorations(vertices)

    return vertices

  def _build_base_shape(self) -> list[VectorPort]:
    """
    Build basic trapezoid vertices without decorations.

    Returns:
      List of 4 VectorPort objects in counter-clockwise order

    """
    return self._make_trapezoid_general(self.w1, self.w2, self.h, self.side_left)

  def get_edge_angle(self, edge_index: int) -> float:
    """
    Get the angle of a specific edge for notch calculations.

    This is the KEY FIX for trapezoid notch alignment. Each edge returns its actual
    angle so notches can align properly instead of being perpendicular.

    Args:
      edge_index: Index of the edge (0=bottom, 1=right, 2=top, 3=left)

    Returns:
      Angle in radians from horizontal for the specified edge

    Edge angles for trapezoids:
    - Bottom (0) and top (2): Always horizontal (0 radians)
    - Left (3) and right (1): Calculated from trapezoid geometry

    """
    if edge_index == 0:  # Bottom edge (always horizontal)
      return 0.0
    elif edge_index == 2:  # Top edge (always horizontal)
      return 0.0
    elif edge_index == 1:  # Right edge
      return self._calculate_right_edge_angle()
    elif edge_index == 3:  # Left edge
      return self._calculate_left_edge_angle()
    else:
      raise ValueError(f'Invalid edge_index: {edge_index}. Must be 0-3.')

  def _calculate_left_edge_angle(self) -> float:
    """
    Calculate the angle of the left edge from horizontal.

    Returns:
      Angle in radians (positive = counterclockwise from horizontal)

    """
    if self.variant == TrapezoidEnum.RIGHT_ANGLE:
      # Right-angle trapezoid: left edge is vertical
      return math.pi / 2  # 90 degrees

    # For general and isosceles trapezoids, calculate from geometry
    # Left slant is determined by the trapezoid construction
    if self.side_left is None:
      # Isosceles case: symmetric, so left edge angle based on width difference
      width_diff = self.w1 - self.w2
      left_slant = width_diff / 2  # Symmetric distribution
    else:
      # General case with specified left side
      left_slant = self._calc_slant_from_side(self.h, self.side_left)

    # Calculate angle from horizontal using rise/run
    # Positive angle = counterclockwise from horizontal
    if left_slant == 0:
      return math.pi / 2  # Vertical
    else:
      return math.atan2(self.h, left_slant)

  def _calculate_right_edge_angle(self) -> float:
    """
    Calculate the angle of the right edge from horizontal.

    Returns:
      Angle in radians (positive = counterclockwise from horizontal)

    """
    # Calculate right slant based on left slant and width difference
    if self.side_left is None:
      # Isosceles case: symmetric
      width_diff = self.w1 - self.w2
      left_slant = width_diff / 2
    else:
      # General case
      left_slant = self._calc_slant_from_side(self.h, self.side_left)

    right_slant = left_slant + self.w1 - self.w2

    # Calculate angle from horizontal
    # Right edge goes from (w1, 0) to (right_slant + w2, h)
    # So the direction vector is (right_slant + w2 - w1, h) = (right_slant - (w1 - w2), h)
    delta_x = right_slant - (self.w1 - self.w2)
    delta_y = self.h

    return math.atan2(delta_y, delta_x)

  def _apply_decorations(self, vertices: list[VectorPort]) -> list[VectorPort]:
    """
    Apply torn edges and notches to the base trapezoid.

    Args:
      vertices: Base trapezoid vertices

    Returns:
      Decorated vertices

    """
    # Identify overlap between torn and notch sides
    torn_sides_set = set(self.torn_sides) if self.torn_sides else set()
    notch_sides_set = set(self.notch_sides) if self.notch_sides else set()

    # Remove NONE values
    torn_sides_set.discard(OrdinalEnum.NONE)
    notch_sides_set.discard(OrdinalEnum.NONE)

    # Find sides that have both torn edges and notches
    torn_notch_sides = torn_sides_set & notch_sides_set

    # Apply processing based on configuration
    if torn_notch_sides and self.noise:
      # Apply mixed processing for torn notches
      vertices = self._apply_torn_and_clean_processing(
        vertices,
        torn_sides_set - torn_notch_sides,  # Torn-only sides
        notch_sides_set - torn_notch_sides,  # Clean notch-only sides
        torn_notch_sides,  # Torn notch sides
      )
    else:
      # Existing paths
      if torn_sides_set and self.noise:
        vertices = self._apply_torn_edges(vertices)

      if notch_sides_set:
        vertices = self._apply_notches(vertices)

    return vertices

  def _apply_torn_and_clean_processing(
    self,
    vertices: list[VectorPort],
    torn_only_sides: set[OrdinalEnum],
    clean_notch_sides: set[OrdinalEnum],
    torn_notch_sides: set[OrdinalEnum],
  ) -> list[VectorPort]:
    """
    Apply mixed processing: torn edges, clean notches, and torn notches.

    Args:
      vertices: Base trapezoid vertices
      torn_only_sides: Sides with torn edges only
      clean_notch_sides: Sides with clean notches only
      torn_notch_sides: Sides with both torn edges and notches

    Returns:
      List of processed vertices

    """
    if len(vertices) != 4:
      raise ValueError('Mixed processing only supported for quadrilaterals (4 vertices)')

    # Define edges in counter-clockwise order
    edges = [
      (OrdinalEnum.SOUTH, vertices[0], vertices[1], 0),  # South: bottom edge
      (OrdinalEnum.EAST, vertices[1], vertices[2], 1),  # East: right edge
      (OrdinalEnum.NORTH, vertices[2], vertices[3], 2),  # North: top edge
      (OrdinalEnum.WEST, vertices[3], vertices[0], 3),  # West: left edge
    ]

    # Collect all points for the final shape
    all_points = []

    for side_enum, start_point, end_point, edge_index in edges:
      if side_enum in torn_notch_sides:
        # Apply torn notch (or just torn edge if notch size/depth is zero)
        if self.notch_size > 0 and self.notch_depth > 0:
          points = self._create_torn_notch(start_point, end_point, side_enum)
          all_points.extend(points[1:])  # Skip first to avoid duplication
        else:
          # No notch, just apply torn edge
          edge_points = self._apply_torn_edge_single(start_point, end_point, side_enum)
          all_points.extend(edge_points[1:])  # Skip first to avoid duplication
      elif side_enum in torn_only_sides:
        # Apply torn edge only
        edge_points = self._apply_torn_edge_single(start_point, end_point, side_enum)
        all_points.extend(edge_points[1:])  # Skip first to avoid duplication
      elif side_enum in clean_notch_sides:
        # Apply clean notch with proper angle alignment
        all_points.append(start_point)
        notch_points = self._create_notch(start_point, end_point, edge_index, side_enum)
        if notch_points:
          all_points.extend(notch_points)
      else:
        # Straight edge
        all_points.append(end_point)

    return all_points

  def _apply_torn_edge_single(
    self, start_point: VectorPort, end_point: VectorPort, side_enum: OrdinalEnum
  ) -> list[VectorPort]:
    """Apply torn edge to a single edge."""
    if not self.noise:
      return [start_point, end_point]

    from ..geo_util import GeoUtil

    side_str = side_enum.name[0]  # Get first letter (N, S, E, W)
    adjusted_amplitude = GeoUtil.get_fitting_amplitude(self.noise_amplitude, side_str)
    scaled_noise = GeoUtil.create_scaled_noise(self.noise, adjusted_amplitude)

    return GeoUtil.create_torn_edge(
      start_point, end_point, scaled_noise, self.noise_segments, self.smoothing_factor
    )

  def _validate_dimensions(self) -> None:
    """Validate that trapezoid dimensions are positive and geometrically valid."""
    self._validate_dimension(self.w1, 'Bottom width (w1)', min_val=0.0, max_val=1.0)
    self._validate_dimension(self.w2, 'Top width (w2)', min_val=0.0, max_val=1.0)
    self._validate_dimension(self.h, 'Height', min_val=0.0, max_val=1.0)

    # Additional trapezoid-specific validation
    if self.side_left is not None:
      if self.side_left < self.h:
        raise ValueError(f'Left side length ({self.side_left}) must be >= height ({self.h})')

      # Validate that the specified left side is geometrically reasonable
      # The max possible side is when it goes from bottom-left to top-right corner
      max_left_side = math.sqrt(self.h**2 + (self.w1) ** 2)  # Diagonal of full rectangle
      if self.side_left > max_left_side * 1.2:  # Allow 20% tolerance for flexibility
        raise ValueError(
          f'Left side length ({self.side_left}) is too large for '
          f'w1={self.w1}, w2={self.w2}, h={self.h}. Maximum reasonable: {max_left_side:.3f}'
        )
