"""Notches mixin for applying rectangular indentations with angle awareness."""

from __future__ import annotations

from modgud.domain.enums import OrdinalEnum
from modgud.domain.ports import VectorPort
from modgud.util.geo import GeoUtil


class NotchesMixin:
  """Mixin for applying notch effects with angle awareness.

  This mixin provides functionality to create rectangular indentations (notches)
  along shape edges, with proper angle alignment for slanted edges like trapezoids.

  Key improvement: Uses get_edge_angle() from the host shape class to align
  notch sides with the shape's edge angles instead of always using perpendicular.
  """

  def _apply_notches(self, vertices: list[VectorPort]) -> list[VectorPort]:
    """Apply notches to specified sides of the shape with angle awareness.

    Args:
      vertices: Base shape vertices (assumed to be 4-vertex quadrilateral)

    Returns:
      List of vertices with notches applied

    Requires these attributes from the host class:
      - notch_sides: list[OrdinalEnum]
      - notch_size: float
      - notch_depth: float
      - notch_offset: float
      - get_edge_angle(edge_index: int) -> float method

    """
    if len(vertices) != 4:
      raise ValueError('Notches only supported for quadrilaterals (4 vertices)')

    notch_sides = getattr(self, 'notch_sides', [])
    notch_size = getattr(self, 'notch_size', 0.0)
    notch_depth = getattr(self, 'notch_depth', 0.0)

    if not notch_sides or notch_size <= 0 or notch_depth <= 0:
      return list(vertices)

    # Convert notch_sides list to set for efficient lookup
    notch_sides_set = set(notch_sides)
    notch_sides_set.discard(OrdinalEnum.NONE)  # Remove NONE if present

    # Early return if no valid notches to apply
    if not notch_sides_set:
      return list(vertices)

    # Define edges in counter-clockwise order
    # Quadrilateral vertices: bottom-left, bottom-right, top-right, top-left
    edges = [
      (
        OrdinalEnum.SOUTH,
        vertices[0],
        vertices[1],
        0,
      ),  # South: bottom-left to bottom-right, edge 0
      (OrdinalEnum.EAST, vertices[1], vertices[2], 1),  # East: bottom-right to top-right, edge 1
      (OrdinalEnum.NORTH, vertices[2], vertices[3], 2),  # North: top-right to top-left, edge 2
      (OrdinalEnum.WEST, vertices[3], vertices[0], 3),  # West: top-left to bottom-left, edge 3
    ]

    # Collect all points for the final shape
    all_points = []

    for side_enum, start_point, end_point, edge_index in edges:
      if side_enum in notch_sides_set:
        # Get adjusted offset for this side
        adjusted_offset = self._get_adjusted_offset(side_enum)

        # Get edge angle from the shape class for proper notch alignment
        edge_angle = self._get_edge_angle_safe(edge_index)

        # Calculate angle-aware notch points
        if hasattr(GeoUtil, 'calculate_angled_notch_points'):
          # Use new angle-aware method if available
          notch_points = GeoUtil.calculate_angled_notch_points(
            start_point, end_point, notch_size, notch_depth, adjusted_offset, edge_angle
          )
        else:
          # Fall back to perpendicular notches
          notch_points = GeoUtil.calculate_notch_points(
            start_point, end_point, notch_size, notch_depth, adjusted_offset
          )

        if notch_points:
          # Add start point
          all_points.append(start_point)
          # Add notch points
          all_points.extend(notch_points)
        else:
          # If notch calculation failed, add straight edge
          all_points.append(start_point)
      else:
        # No notch on this side - just add the start point
        all_points.append(start_point)

    # Handle corner notches (for diagonal notches like NORTHEAST, etc.)
    return self._apply_corner_notches(all_points, vertices, notch_sides_set)

  def _create_notch(
    self, start: VectorPort, end: VectorPort, edge_index: int, side_enum: OrdinalEnum
  ) -> list[VectorPort]:
    """Create notch with proper angle alignment for the given edge.

    Args:
      start: Start point of edge
      end: End point of edge
      edge_index: Index of the edge for angle calculation
      side_enum: The side enum for offset calculation

    Returns:
      List of points forming the notch, or original points if torn notch

    """
    notch_size = getattr(self, 'notch_size', 0.1)
    notch_depth = getattr(self, 'notch_depth', 0.0)

    if notch_size <= 0 or notch_depth <= 0:
      return [start, end]

    # Check if this is a torn notch (both torn and notched)
    torn_sides = getattr(self, 'torn_sides', [])
    torn_sides_set = set(torn_sides)
    torn_sides_set.discard(OrdinalEnum.NONE)

    if side_enum in torn_sides_set and hasattr(self, '_create_torn_notch'):
      return self._create_torn_notch(start, end, side_enum)
    else:
      # Create clean notch with angle awareness
      adjusted_offset = self._get_adjusted_offset(side_enum)
      edge_angle = self._get_edge_angle_safe(edge_index)

      if hasattr(GeoUtil, 'calculate_angled_notch_points'):
        return GeoUtil.calculate_angled_notch_points(
          start, end, notch_size, notch_depth, adjusted_offset, edge_angle
        )
      else:
        return GeoUtil.calculate_notch_points(start, end, notch_size, notch_depth, adjusted_offset)

  def _get_edge_angle_safe(self, edge_index: int) -> float:
    """Safely get edge angle from the shape class.

    Args:
      edge_index: Index of the edge

    Returns:
      Edge angle in radians, or 0.0 if get_edge_angle not available

    """
    if hasattr(self, 'get_edge_angle'):
      try:
        return self.get_edge_angle(edge_index)
      except (AttributeError, NotImplementedError):
        pass

    # Default to perpendicular (0 radians = horizontal)
    return 0.0

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

  def _apply_corner_notches(
    self,
    all_points: list[VectorPort],
    vertices: list[VectorPort],
    notch_sides_set: set[OrdinalEnum],
  ) -> list[VectorPort]:
    """Apply corner notches by modifying existing vertices.

    Args:
      all_points: Current list of shape points
      vertices: Original quadrilateral vertices
      notch_sides_set: Set of sides with notches

    Returns:
      Modified list of points with corner notches applied

    Note:
      Corner notches (NORTHEAST, NORTHWEST, etc.) create indentations at corners
      rather than along edges. This is less commonly used but supported for completeness.

    """
    # Handle corner notches - these modify existing vertices
    corner_notches = {
      OrdinalEnum.NORTHEAST: vertices[2],  # Top-right corner
      OrdinalEnum.NORTHWEST: vertices[3],  # Top-left corner
      OrdinalEnum.SOUTHEAST: vertices[1],  # Bottom-right corner
      OrdinalEnum.SOUTHWEST: vertices[0],  # Bottom-left corner
    }

    # Check if any corner notches are requested
    corner_notch_sides = notch_sides_set.intersection(corner_notches.keys())

    if not corner_notch_sides:
      return all_points

    # For now, corner notches just return the points unchanged
    # This could be enhanced to actually create corner indentations
    # but is not commonly used in practice
    return all_points
