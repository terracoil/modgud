"""Torn edges mixin for applying noise-based edge distortion."""

from __future__ import annotations

from typing import TYPE_CHECKING

from modgud.domain.enums import OrdinalEnum
from modgud.domain.ports import VectorPort
from modgud.util.geo import GeoUtil, Vector

if TYPE_CHECKING:
  pass


class TornEdgesMixin:
  """Mixin for applying torn edge effects using noise to create organic, hand-drawn appearance.

  This mixin provides functionality to transform straight edges into irregular,
  torn-looking edges using configurable noise parameters.

  Uses margin-based approach: torn edges are positioned inward by the amplitude value,
  ensuring noise displacement stays within bounds naturally without clamping.
  """

  def _apply_torn_edges(self, vertices: list[VectorPort]) -> list[VectorPort]:
    """Apply torn edges to shape vertices using noise with margin-based positioning.

    For torn edges, the base edge is positioned inward by the noise amplitude.
    This ensures that noise displacement naturally stays within bounds without
    needing to clamp, preserving the natural torn paper aesthetic.

    Args:
      vertices: Base shape vertices (assumed to be 4-vertex quadrilateral)

    Returns:
      List of vertices with torn edges applied

    Requires these attributes from the host class:
      - torn_sides: list[OrdinalEnum]
      - noise: NoisePort
      - noise_amplitude: float
      - noise_segments: int
      - smoothing_factor: float

    """
    if len(vertices) != 4:
      raise ValueError('Torn edges only supported for quadrilaterals (4 vertices)')

    torn_sides = getattr(self, 'torn_sides', [])
    noise = getattr(self, 'noise', None)

    if not torn_sides or not noise:
      return list(vertices)

    # Convert torn_sides list to set for efficient lookup
    torn_sides_set = set(torn_sides)
    torn_sides_set.discard(OrdinalEnum.NONE)  # Remove NONE if present

    if not torn_sides_set:
      return list(vertices)

    noise_amplitude = getattr(self, 'noise_amplitude', 5.0)
    noise_segments = getattr(self, 'noise_segments', 100)
    smoothing_factor = getattr(self, 'smoothing_factor', 0.1)

    # Calculate shape bounds from vertices
    min_x = min(v.x for v in vertices)
    max_x = max(v.x for v in vertices)
    min_y = min(v.y for v in vertices)
    max_y = max(v.y for v in vertices)

    # Calculate inset vertices based on which sides are torn
    # This creates the margin that allows noise displacement to stay within bounds
    inset_vertices = self._calculate_inset_vertices(
      vertices, torn_sides_set, noise_amplitude, min_x, max_x, min_y, max_y
    )

    # Define edges in clockwise order matching the vertex ordering
    # Quadrilateral vertices are: bottom-left, bottom-right, top-right, top-left
    edges = [
      (
        OrdinalEnum.NORTH,
        inset_vertices[3],
        inset_vertices[2],
        'top',
      ),  # North: top-left to top-right
      (
        OrdinalEnum.EAST,
        inset_vertices[1],
        inset_vertices[2],
        'right',
      ),  # East: bottom-right to top-right
      (
        OrdinalEnum.SOUTH,
        inset_vertices[0],
        inset_vertices[1],
        'bottom',
      ),  # South: bottom-left to bottom-right
      (
        OrdinalEnum.WEST,
        inset_vertices[0],
        inset_vertices[3],
        'left',
      ),  # West: bottom-left to top-left
    ]

    # Collect all points for the final shape
    all_points: list[VectorPort] = []

    for side_enum, start_point, end_point, _edge_name in edges:
      if side_enum in torn_sides_set:
        # Create torn edge with adjusted amplitude
        side_str = side_enum.name[0]  # Get first letter (N, S, E, W)
        adjusted_amplitude = GeoUtil.get_fitting_amplitude(noise_amplitude, side_str)
        scaled_noise = GeoUtil.create_scaled_noise(noise, adjusted_amplitude)

        # Create torn edge points (excluding start to avoid duplication)
        edge_points = GeoUtil.create_torn_edge(
          start_point,
          end_point,
          scaled_noise,
          noise_segments,
          smoothing_factor,
        )
        all_points.extend(edge_points[1:])  # Skip first point to avoid duplication
      else:
        # Straight edge - just add the end point
        all_points.append(end_point)

    return all_points

  def _calculate_inset_vertices(
    self,
    vertices: list[VectorPort],
    torn_sides_set: set[OrdinalEnum],
    amplitude: float,
    min_x: float,
    max_x: float,
    min_y: float,
    max_y: float,
  ) -> list[VectorPort]:
    """Calculate inset vertices based on which sides are torn.

    Each torn side's vertices are moved inward by the amplitude, creating
    a margin that allows noise displacement to stay within bounds.

    Args:
      vertices: Original quadrilateral vertices [bottom-left, bottom-right, top-right, top-left]
      torn_sides_set: Set of sides that will have torn edges
      amplitude: Noise amplitude (determines inset distance)
      min_x: Minimum X bound of original shape
      max_x: Maximum X bound of original shape
      min_y: Minimum Y bound of original shape
      max_y: Maximum Y bound of original shape

    Returns:
      Inset vertices with margins applied for torn sides

    """
    # Calculate relative amplitude as fraction of shape dimensions
    width = max_x - min_x
    height = max_y - min_y

    # Convert amplitude to relative units (shapes use 0-1 coordinate space)
    rel_amplitude_x = amplitude / width if width > 0 else 0.0
    rel_amplitude_y = amplitude / height if height > 0 else 0.0

    # Calculate inset amounts for each side
    north_inset = rel_amplitude_y if OrdinalEnum.NORTH in torn_sides_set else 0.0
    south_inset = rel_amplitude_y if OrdinalEnum.SOUTH in torn_sides_set else 0.0
    east_inset = rel_amplitude_x if OrdinalEnum.EAST in torn_sides_set else 0.0
    west_inset = rel_amplitude_x if OrdinalEnum.WEST in torn_sides_set else 0.0

    # Apply insets to vertices
    # vertices: [bottom-left, bottom-right, top-right, top-left]
    inset_vertices = [
      # Bottom-left: affected by South and West
      Vector(
        vertices[0].x + west_inset,
        vertices[0].y + south_inset,
        vertices[0].z,
        vertices[0].w,
        name=vertices[0].name,
      ),
      # Bottom-right: affected by South and East
      Vector(
        vertices[1].x - east_inset,
        vertices[1].y + south_inset,
        vertices[1].z,
        vertices[1].w,
        name=vertices[1].name,
      ),
      # Top-right: affected by North and East
      Vector(
        vertices[2].x - east_inset,
        vertices[2].y - north_inset,
        vertices[2].z,
        vertices[2].w,
        name=vertices[2].name,
      ),
      # Top-left: affected by North and West
      Vector(
        vertices[3].x + west_inset,
        vertices[3].y - north_inset,
        vertices[3].z,
        vertices[3].w,
        name=vertices[3].name,
      ),
    ]

    return inset_vertices

  def _apply_noise_to_edge(
    self, start: VectorPort, end: VectorPort, segments: int, amplitude_factor: float = 0.5
  ) -> list[VectorPort]:
    """Apply noise to a single edge with configurable amplitude scaling.

    Args:
      start: Start point of edge
      end: End point of edge
      segments: Number of segments for noise application
      amplitude_factor: Scale factor for noise amplitude (default 0.5 for notch edges)

    Returns:
      List of points forming the noisy edge

    """
    noise = getattr(self, 'noise', None)
    if not noise:
      return [start, end]

    noise_amplitude = getattr(self, 'noise_amplitude', 5.0)
    smoothing_factor = getattr(self, 'smoothing_factor', 0.1)

    # Use scaled amplitude
    adjusted_amplitude = noise_amplitude * amplitude_factor
    scaled_noise = GeoUtil.create_scaled_noise(noise, adjusted_amplitude)

    return GeoUtil.create_torn_edge(start, end, scaled_noise, segments, smoothing_factor)

  def _create_torn_notch(
    self, start_point: VectorPort, end_point: VectorPort, side_enum: OrdinalEnum
  ) -> list[VectorPort]:
    """Create a notch with torn edges using noise.

    Args:
      start_point: Start point of the edge
      end_point: End point of the edge
      side_enum: Which side the notch is on

    Returns:
      List of points forming the torn notch

    """
    # Get notch parameters
    notch_size = getattr(self, 'notch_size', 0.1)
    notch_depth = getattr(self, 'notch_depth', 0.0)

    if notch_size <= 0 or notch_depth <= 0:
      return [start_point, end_point]

    # Calculate notch corner points (same as clean notch)
    adjusted_offset = self._get_adjusted_offset(side_enum)
    notch_points = GeoUtil.calculate_notch_points(
      start_point, end_point, notch_size, notch_depth, adjusted_offset
    )

    if not notch_points or len(notch_points) != 4:
      return [start_point, end_point]

    # Apply noise to each edge of the notch
    result_points = [start_point]

    # Left edge of notch (from outer to inner)
    left_edge = self._apply_noise_to_edge(notch_points[0], notch_points[1], segments=8)
    result_points.extend(left_edge[1:])

    # Inner edge of notch (parallel to main edge)
    inner_edge = self._apply_noise_to_edge(notch_points[1], notch_points[2], segments=15)
    result_points.extend(inner_edge[1:])

    # Right edge of notch (from inner to outer)
    right_edge = self._apply_noise_to_edge(notch_points[2], notch_points[3], segments=8)
    result_points.extend(right_edge[1:])

    return result_points

  def _get_adjusted_offset(self, side_enum: OrdinalEnum) -> float:
    """Get adjusted offset for a side, accounting for edge direction.

    Args:
      side_enum: The side to get offset for

    Returns:
      Adjusted offset value

    """
    notch_offset = getattr(self, 'notch_offset', 0.0)

    # Adjust offset for edges that go right-to-left or bottom-to-top
    # to match user expectations (positive offset = right/up)
    if side_enum in (OrdinalEnum.NORTH, OrdinalEnum.WEST):
      return -notch_offset
    return notch_offset
