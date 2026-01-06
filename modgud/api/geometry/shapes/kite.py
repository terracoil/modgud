"""Kite shape with two pairs of adjacent sides equal and perpendicular diagonals."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, Sequence

from modgud.domain.enums import OrdinalEnum
from modgud.domain.ports import VectorPort

from .base import ShapeBase
from .mixins import NotchesMixin, TornEdgesMixin, ValidationMixin

if TYPE_CHECKING:
  from modgud.domain.ports.noise_port import NoisePort


@dataclass(frozen=True)
class Kite(ShapeBase, ValidationMixin, TornEdgesMixin, NotchesMixin):
  """
  Kite shape with two pairs of adjacent sides equal and perpendicular diagonals.

  A kite has two pairs of adjacent sides that are equal in length.
  The diagonals are perpendicular, with one diagonal bisecting the other.
  Defined by the lengths of the two diagonals.
  """

  # Required geometric parameters
  diagonal1: float  # Length of first diagonal (vertical)
  diagonal2: float  # Length of second diagonal (horizontal)

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
    """
    Build kite shape with optional decorations.

    Returns:
      Sequence of VectorPort objects defining the kite boundary

    """
    # Start with base kite
    vertices = self._build_base_shape()

    # Apply decorations
    vertices = self._apply_decorations(vertices)

    return vertices

  def _build_base_shape(self) -> list[VectorPort]:
    """
    Build basic kite vertices without decorations.

    Returns:
      List of 4 VectorPort objects in counter-clockwise order

    """
    # Kite is constructed from two perpendicular diagonals intersecting
    # Center the kite at origin of the coordinate system
    half_d1 = self.diagonal1 / 2  # Half of vertical diagonal
    half_d2 = self.diagonal2 / 2  # Half of horizontal diagonal

    # Kite vertices: top, right, bottom, left
    coords = [
      (half_d2, 0),  # Right vertex
      (0, half_d1),  # Top vertex
      (-half_d2, 0),  # Left vertex
      (0, -half_d1),  # Bottom vertex
    ]

    # Translate to positive quadrant and scale to fit in unit square
    # Find bounding box
    min_x = min(x for x, y in coords)
    max_x = max(x for x, y in coords)
    min_y = min(y for x, y in coords)
    max_y = max(y for x, y in coords)

    width = max_x - min_x
    height = max_y - min_y

    # Translate to origin and scale to fit in unit square
    translated_coords = []
    for x, y in coords:
      new_x = (x - min_x) / width
      new_y = (y - min_y) / height
      translated_coords.append((new_x, new_y))

    return self._make_points(translated_coords)

  def get_edge_angle(self, edge_index: int) -> float:
    """
    Get the angle of a specific edge for notch calculations.

    Args:
      edge_index: Index of the edge (0=bottom, 1=right, 2=top, 3=left)

    Returns:
      Angle in radians from horizontal for the specified edge

    """
    # Calculate kite geometry for angle determination
    half_d1 = self.diagonal1 / 2
    half_d2 = self.diagonal2 / 2

    # Calculate angles based on kite geometry
    # The kite has 4 edges connecting the diagonal endpoints

    if edge_index == 0:  # Bottom edge: from right to bottom
      return math.atan2(-half_d1, -half_d2)
    elif edge_index == 1:  # Right edge: from bottom to left
      return math.atan2(half_d1, -half_d2)
    elif edge_index == 2:  # Top edge: from left to top
      return math.atan2(half_d1, half_d2)
    elif edge_index == 3:  # Left edge: from top to right
      return math.atan2(-half_d1, half_d2)
    else:
      raise ValueError(f'Invalid edge_index: {edge_index}. Must be 0-3.')

  def _apply_decorations(self, vertices: list[VectorPort]) -> list[VectorPort]:
    """
    Apply torn edges and notches to the base kite.

    Args:
      vertices: Base kite vertices

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
    """Apply mixed processing for kite."""
    if len(vertices) != 4:
      raise ValueError('Mixed processing only supported for quadrilaterals (4 vertices)')

    # Define edges in counter-clockwise order
    # Note: Kite vertex order may be different, map appropriately
    edges = [
      (OrdinalEnum.SOUTH, vertices[0], vertices[1], 0),  # First edge
      (OrdinalEnum.EAST, vertices[1], vertices[2], 1),  # Second edge
      (OrdinalEnum.NORTH, vertices[2], vertices[3], 2),  # Third edge
      (OrdinalEnum.WEST, vertices[3], vertices[0], 3),  # Fourth edge
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

    from ..geo_util import GeoUtil

    side_str = side_enum.name[0]  # Get first letter (N, S, E, W)
    adjusted_amplitude = GeoUtil.get_fitting_amplitude(self.noise_amplitude, side_str)
    scaled_noise = GeoUtil.create_scaled_noise(self.noise, adjusted_amplitude)

    return GeoUtil.create_torn_edge(
      start_point, end_point, scaled_noise, self.noise_segments, self.smoothing_factor
    )

  def _validate_dimensions(self) -> None:
    """Validate that kite diagonals are positive and within range."""
    self._validate_dimension(self.diagonal1, 'Diagonal1 length', min_val=0.0, max_val=1.0)
    self._validate_dimension(self.diagonal2, 'Diagonal2 length', min_val=0.0, max_val=1.0)

    # For kite, ensure the resulting shape fits reasonably in unit square
    # The diagonals define the bounding box
    max_dimension = max(self.diagonal1, self.diagonal2)
    if max_dimension > 1.0:
      raise ValueError(
        f'Kite with diagonals {self.diagonal1}, {self.diagonal2} is too large. '
        f'Max diagonal should be ≤ 1.0'
      )
