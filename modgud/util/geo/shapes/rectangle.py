"""Rectangle shape with opposite sides equal and all angles 90 degrees."""

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
class Rectangle(ShapeBase, ValidationMixin, TornEdgesMixin, NotchesMixin):
  """Rectangle shape with opposite sides equal and 90-degree angles.

  A rectangle has opposite sides of equal length and all angles at 90 degrees.
  Width and height can be different, making it more general than a square.
  Supports torn edges and notches as decorative features.
  """

  # Required geometric parameters
  width: float
  height: float

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
    """Build rectangle shape with optional decorations.

    Returns:
      Sequence of VectorPort objects defining the rectangle boundary

    """
    # Start with base rectangle
    vertices = self._build_base_shape()

    # Apply decorations
    vertices = self._apply_decorations(vertices)

    return vertices

  def _build_base_shape(self) -> list[VectorPort]:
    """Build basic rectangle vertices without decorations.

    Returns:
      List of 4 VectorPort objects in counter-clockwise order:
      [(0,0), (width,0), (width,height), (0,height)]

    """
    return self._make_rect_aligned(self.width, self.height)

  def get_edge_angle(self, edge_index: int) -> float:
    """Get the angle of a specific edge for notch calculations.

    Args:
      edge_index: Index of the edge (0=bottom, 1=right, 2=top, 3=left)

    Returns:
      Angle in radians (all edges are perpendicular for rectangles)

    For rectangles, all edges are axis-aligned:
    - Bottom and top edges: 0 radians (horizontal)
    - Left and right edges: π/2 radians (vertical)

    """
    if edge_index in (0, 2):  # Bottom and top edges
      return 0.0  # Horizontal
    elif edge_index in (1, 3):  # Right and left edges
      return math.pi / 2  # Vertical
    else:
      raise ValueError(f'Invalid edge_index: {edge_index}. Must be 0-3.')

  def _apply_decorations(self, vertices: list[VectorPort]) -> list[VectorPort]:
    """Apply torn edges and notches to the base rectangle.

    Args:
      vertices: Base rectangle vertices

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
    """Apply mixed processing: torn edges, clean notches, and torn notches.

    Args:
      vertices: Base rectangle vertices
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
        # Apply clean notch
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

    side_str = side_enum.name[0]  # Get first letter (N, S, E, W)
    adjusted_amplitude = GeoUtil.get_fitting_amplitude(self.noise_amplitude, side_str)
    scaled_noise = GeoUtil.create_scaled_noise(self.noise, adjusted_amplitude)

    return GeoUtil.create_torn_edge(
      start_point, end_point, scaled_noise, self.noise_segments, self.smoothing_factor
    )

  def _validate_dimensions(self) -> None:
    """Validate that width and height are positive and within acceptable range."""
    self._validate_dimension(self.width, 'Width', min_val=0.0, max_val=1.0)
    self._validate_dimension(self.height, 'Height', min_val=0.0, max_val=1.0)
