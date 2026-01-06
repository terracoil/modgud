"""Torn edges mixin for applying noise-based edge distortion."""

from __future__ import annotations

from typing import TYPE_CHECKING

from modgud.domain.enums import OrdinalEnum
from modgud.domain.ports import VectorPort

from ...geo_util import GeoUtil

if TYPE_CHECKING:
  pass


class TornEdgesMixin:
  """
  Mixin for applying torn edge effects using noise to create organic, hand-drawn appearance.

  This mixin provides functionality to transform straight edges into irregular,
  torn-looking edges using configurable noise parameters.
  """

  def _apply_torn_edges(self, vertices: list[VectorPort]) -> list[VectorPort]:
    """
    Apply torn edges to shape vertices using noise.

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

    # Define edges in clockwise order to match TornPaper convention
    # Quadrilateral vertices are typically: bottom-left, bottom-right, top-right, top-left
    edges = [
      (OrdinalEnum.NORTH, vertices[3], vertices[2], 'top'),  # North: top-left to top-right
      (OrdinalEnum.EAST, vertices[1], vertices[2], 'right'),  # East: bottom-right to top-right
      (OrdinalEnum.SOUTH, vertices[0], vertices[1], 'bottom'),  # South: bottom-left to bottom-right
      (OrdinalEnum.WEST, vertices[0], vertices[3], 'left'),  # West: bottom-left to top-left
    ]

    # Collect all points for the final shape
    all_points = []
    noise_amplitude = getattr(self, 'noise_amplitude', 5.0)
    noise_segments = getattr(self, 'noise_segments', 100)
    smoothing_factor = getattr(self, 'smoothing_factor', 0.1)

    for side_enum, start_point, end_point, _edge_name in edges:
      if side_enum in torn_sides_set:
        # Create torn edge with adjusted amplitude
        # Convert enum to string for GeoUtil compatibility
        side_str = side_enum.name[0]  # Get first letter (N, S, E, W)
        adjusted_amplitude = GeoUtil.get_fitting_amplitude(noise_amplitude, side_str)
        scaled_noise = GeoUtil.create_scaled_noise(noise, adjusted_amplitude)

        # Create torn edge points (excluding start to avoid duplication)
        edge_points = GeoUtil.create_torn_edge(
          start_point, end_point, scaled_noise, noise_segments, smoothing_factor
        )
        all_points.extend(edge_points[1:])  # Skip first point to avoid duplication
      else:
        # Straight edge - just add the end point
        all_points.append(end_point)

    return all_points

  def _apply_noise_to_edge(
    self, start: VectorPort, end: VectorPort, segments: int, amplitude_factor: float = 0.5
  ) -> list[VectorPort]:
    """
    Apply noise to a single edge with configurable amplitude scaling.

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
    """
    Create a notch with torn edges using noise.

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
    """
    Get adjusted offset for a side, accounting for edge direction.

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
