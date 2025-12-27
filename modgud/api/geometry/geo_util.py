"""Geometric utility functions and validators."""

from __future__ import annotations

import math

from ...domain.ports.vector_port import VectorPort
from .vector import Vector


class GeoUtil:
  """Utility class providing common geometric calculations and validations."""

  @staticmethod
  def validate_dimension(
    value: float, name: str, min_val: float = 0.0, max_val: float = 1.0, exclusive_min: bool = True
  ) -> None:
    """
    Validate a dimension is within acceptable range.

    :param value: The value to validate
    :param name: Name of the dimension for error messages
    :param min_val: Minimum allowed value
    :param max_val: Maximum allowed value
    :param exclusive_min: If True, min is exclusive; if False, inclusive
    :raises ValueError: If value is outside valid range
    """
    if exclusive_min:
      if not (min_val < value <= max_val):
        raise ValueError(f'{name} must be in range ({min_val}, {max_val}], got {value}')
    else:
      if not (min_val <= value <= max_val):
        raise ValueError(f'{name} must be in range [{min_val}, {max_val}], got {value}')

  @staticmethod
  def calc_slant_from_angle(h: float, angle: float) -> float:
    """
    Calculate horizontal slant offset from height and angle.

    :param h: Height
    :param angle: Angle in degrees
    :returns: Horizontal slant offset
    :raises ValueError: If angle not in (0, 180)
    """
    if not (0 < angle < 180):
      raise ValueError(f'Angle must be in range (0, 180) degrees, got {angle}')
    result = h / math.tan(math.radians(angle))
    return result

  @staticmethod
  def calc_slant_from_side(h: float, side: float) -> float:
    """
    Calculate horizontal slant offset from height and side length.

    :param h: Height
    :param side: Side length
    :returns: Horizontal slant offset
    :raises ValueError: If side < h
    """
    if side < h:
      raise ValueError(f'Side length ({side}) must be >= height ({h})')
    result = math.sqrt(side**2 - h**2)
    return result

  @staticmethod
  def make_points(coords: list[tuple[float, float]]) -> list[VectorPort]:
    """
    Convert coordinate tuples to VectorPort objects.

    :param coords: List of (x, y) tuples
    :returns: List of VectorPort objects
    """
    result = [Vector.from_tuple(coord) for coord in coords]
    return result

  @staticmethod
  def distance(p1: VectorPort, p2: VectorPort) -> float:
    """
    Calculate Euclidean distance between two points.

    :param p1: First point
    :param p2: Second point
    :returns: Distance between points
    """
    dx = p2.x - p1.x
    dy = p2.y - p1.y
    result = math.sqrt(dx * dx + dy * dy)
    return result

  @staticmethod
  def polygon_area(vertices: list[VectorPort]) -> float:
    """
    Calculate polygon area using the shoelace formula.

    Assumes vertices are ordered (clockwise or counterclockwise).

    :param vertices: List of vertices in order
    :returns: Area of the polygon
    """
    if len(vertices) < 3:
      raise ValueError('Polygon must have at least 3 vertices')

    area = 0.0
    n = len(vertices)

    for i in range(n):
      j = (i + 1) % n
      area += vertices[i].x * vertices[j].y
      area -= vertices[j].x * vertices[i].y

    result = abs(area) / 2.0
    return result

  @staticmethod
  def polygon_perimeter(vertices: list[VectorPort]) -> float:
    """
    Calculate polygon perimeter by summing edge distances.

    :param vertices: List of vertices in order
    :returns: Perimeter of the polygon
    """
    if len(vertices) < 2:
      raise ValueError('Polygon must have at least 2 vertices')

    perimeter = 0.0
    n = len(vertices)

    for i in range(n):
      j = (i + 1) % n
      perimeter += GeoUtil.distance(vertices[i], vertices[j])

    return perimeter

  @staticmethod
  def degrees_to_radians(degrees: float) -> float:
    """
    Convert degrees to radians.

    :param degrees: Angle in degrees
    :returns: Angle in radians
    """
    return math.radians(degrees)

  @staticmethod
  def radians_to_degrees(radians: float) -> float:
    """
    Convert radians to degrees.

    :param radians: Angle in radians
    :returns: Angle in degrees
    """
    return math.degrees(radians)
