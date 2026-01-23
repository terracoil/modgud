"""Parallelogram shape with opposite sides parallel and equal."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, Sequence

from modgud.domain.enums import OrdinalEnum
from modgud.domain.ports import VectorPort
from modgud.util.geo import GeoUtil

from .base import ShapeBase
from .mixins import NotchesMixin, TornEdgesMixin, ValidationMixin

if TYPE_CHECKING:
  from modgud.domain.ports import NoisePort


@dataclass(frozen=True)
class Parallelogram(ShapeBase, ValidationMixin, TornEdgesMixin, NotchesMixin):
  """Parallelogram shape with opposite sides parallel and equal.

  A parallelogram has opposite sides that are parallel and equal in length.
  The angles are not necessarily 90 degrees (that would be a rectangle).
  Defined by width, height, and angle (or derived slant).
  """

  # Required geometric parameters
  width: float  # Base width
  height: float  # Perpendicular height
  angle: float  # Angle in radians from horizontal (or use slant if provided)
  slant: Optional[float] = None  # Optional: horizontal offset instead of angle

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

  def __post_init__(self) -> None:
    """Validate parameters after initialization."""
    self._validate_params()

  def build_shape(self) -> Sequence[VectorPort]:
    """Build parallelogram shape with optional decorations.

    Returns:
      Sequence of VectorPort objects defining the parallelogram boundary

    """
    # Start with base parallelogram
    vertices = self._build_base_shape()

    # Apply decorations
    vertices = self._apply_decorations(vertices)

    return vertices

  def _build_base_shape(self) -> list[VectorPort]:
    """Build basic parallelogram vertices without decorations.

    Returns:
      List of 4 VectorPort objects in counter-clockwise order

    """
    # Calculate slant from angle or use provided slant
    if self.slant is not None:
      actual_slant = self.slant
    else:
      actual_slant = self._calc_slant_from_angle(self.height, self.angle)

    return self._make_parallelogram_general(self.width, self.height, actual_slant)

  def get_edge_angle(self, edge_index: int) -> float:
    """Get the angle of a specific edge for notch calculations.

    Args:
      edge_index: Index of the edge (0=bottom, 1=right, 2=top, 3=left)

    Returns:
      Angle in radians from horizontal for the specified edge

    """
    # Calculate actual slant
    if self.slant is not None:
      actual_slant = self.slant
    else:
      actual_slant = self._calc_slant_from_angle(self.height, self.angle)

    if edge_index == 0:  # Bottom edge (horizontal)
      return 0.0
    elif edge_index == 2:  # Top edge (horizontal, parallel to bottom)
      return 0.0
    elif edge_index == 1:  # Right edge
      # Right edge goes from (width, 0) to (width + slant, height)
      return math.atan2(self.height, actual_slant)
    elif edge_index == 3:  # Left edge
      # Left edge goes from (0, 0) to (slant, height)
      return math.atan2(self.height, actual_slant)
    else:
      raise ValueError(f'Invalid edge_index: {edge_index}. Must be 0-3.')

  def _apply_decorations(self, vertices: list[VectorPort]) -> list[VectorPort]:
    """Apply torn edges and notches to the base parallelogram.

    Args:
      vertices: Base parallelogram vertices

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
    """Apply mixed processing for parallelogram."""
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
        if self.notch_size > 0 and self.notch_depth > 0:
          points = self._create_torn_notch(start_point, end_point, side_enum)
          all_points.extend(points[1:])  # Skip first to avoid duplication
        else:
          edge_points = self._apply_torn_edge_single(start_point, end_point, side_enum)
          all_points.extend(edge_points[1:])
      elif side_enum in torn_only_sides:
        edge_points = self._apply_torn_edge_single(start_point, end_point, side_enum)
        all_points.extend(edge_points[1:])
      elif side_enum in clean_notch_sides:
        all_points.append(start_point)
        notch_points = self._create_notch(start_point, end_point, edge_index, side_enum)
        if notch_points:
          all_points.extend(notch_points)
      else:
        all_points.append(end_point)

    return all_points

  def _apply_torn_edge_single(
    self, start_point: VectorPort, end_point: VectorPort, side_enum: OrdinalEnum
  ) -> list[VectorPort]:
    """Apply torn edge to a single edge."""
    if not self.noise:
      return [start_point, end_point]

    side_str = side_enum.name[0]  # Get first letter (N, S, E, W)
    adjusted_amplitude = GeoUtil.get_fitting_amplitude(self.noise_amplitude, side_str)
    scaled_noise = GeoUtil.create_scaled_noise(self.noise, adjusted_amplitude)

    return GeoUtil.create_torn_edge(
      start_point, end_point, scaled_noise, self.noise_segments, self.smoothing_factor
    )

  def _validate_dimensions(self) -> None:
    """Validate that parallelogram dimensions are positive and within range."""
    self._validate_dimension(self.width, 'Width', min_val=0.0, max_val=1.0)
    self._validate_dimension(self.height, 'Height', min_val=0.0, max_val=1.0)

    # Validate angle is reasonable (not too close to 0 or π which would collapse the shape)
    if abs(self.angle) < 0.1 or abs(self.angle - math.pi) < 0.1:
      raise ValueError(
        f'Angle {self.angle:.3f} rad ({math.degrees(self.angle):.1f}°) too close to 0° or 180°'
      )

    # If slant is provided, validate it's reasonable
    if self.slant is not None:
      max_reasonable_slant = 2.0 * self.width  # Allow up to 2x width offset
      if abs(self.slant) > max_reasonable_slant:
        raise ValueError(
          f'Slant {self.slant} is too large (max reasonable: ±{max_reasonable_slant:.3f})'
        )
