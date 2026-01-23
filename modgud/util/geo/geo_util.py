"""Geometric utility functions and validators."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from modgud.domain.ports import VectorPort

from .vector import Vector

if TYPE_CHECKING:
  from modgud.domain.ports import NoisePort


class GeoUtil:
  """Utility class providing common geometric calculations and validations."""

  @staticmethod
  def validate_dimension(
    value: float, name: str, min_val: float = 0.0, max_val: float = 1.0, exclusive_min: bool = True
  ) -> None:
    """Validate a dimension is within acceptable range.

    :param value: The name to validate
    :param name: Name of the dimension for error messages
    :param min_val: Minimum allowed name
    :param max_val: Maximum allowed name
    :param exclusive_min: If True, min is exclusive; if False, inclusive
    :raises ValueError: If name is outside valid range
    """
    if exclusive_min:
      if not (min_val < value <= max_val):
        raise ValueError(f'{name} must be in range ({min_val}, {max_val}], got {value}')
    else:
      if not (min_val <= value <= max_val):
        raise ValueError(f'{name} must be in range [{min_val}, {max_val}], got {value}')

  @staticmethod
  def calc_slant_from_angle(h: float, angle: float) -> float:
    """Calculate horizontal slant offset from height and angle.

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
    """Calculate horizontal slant offset from height and side length.

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
    """Convert coordinate tuples to VectorPort objects.

    :param coords: List of (x, y) tuples
    :returns: List of VectorPort objects
    """
    result = [Vector.from_tuple(coord) for coord in coords]
    return result

  @staticmethod
  def distance(p1: VectorPort, p2: VectorPort) -> float:
    """Calculate Euclidean distance between two points.

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
    """Calculate polygon area using the shoelace formula.

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
    """Calculate polygon perimeter by summing edge distances.

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
    """Convert degrees to radians.

    :param degrees: Angle in degrees
    :returns: Angle in radians
    """
    return math.radians(degrees)

  @staticmethod
  def radians_to_degrees(radians: float) -> float:
    """Convert radians to degrees.

    :param radians: Angle in radians
    :returns: Angle in degrees
    """
    return math.degrees(radians)

  @staticmethod
  def validate_torn_sides(torn_sides: str) -> None:
    """Validate torn_sides parameter contains only valid side characters.

    :param torn_sides: String containing side characters (N/S/E/W)
    :raises ValueError: If torn_sides contains invalid characters
    """
    if not torn_sides:
      return  # Empty string is valid (no torn sides)

    valid_sides = set('NSEW')
    torn_upper = torn_sides.upper()
    if not all(s in valid_sides for s in torn_upper):
      raise ValueError("torn_sides must contain only 'N', 'S', 'E', 'W' characters")

  @staticmethod
  def get_fitting_amplitude(base_amplitude: float, side: str) -> float:
    """Get amplitude with proper sign for fitting constraints.

    North and South edges must have opposite tear directions for fitting.
    East and West edges must have opposite tear directions for fitting.

    :param base_amplitude: Base amplitude name
    :param side: Side character (N/S/E/W)
    :returns: Amplitude with proper sign
    """
    fitting_signs = {
      'N': 1,  # North tears away from center
      'S': -1,  # South tears opposite to North
      'E': 1,  # East tears away from center
      'W': -1,  # West tears opposite to East
    }
    return base_amplitude * fitting_signs[side]

  @staticmethod
  def create_scaled_noise(base_noise: 'NoisePort', amplitude: float) -> 'NoisePort':
    """Create a noise instance with scaled amplitude.

    :param base_noise: Base noise provider
    :param amplitude: Scaling amplitude
    :returns: Noise provider with scaled output
    """

    # Create a wrapper that scales the noise output
    class ScaledNoise:
      def __init__(self, base_noise: 'NoisePort', scale: float):
        self.base_noise = base_noise
        self.scale = scale

      def noise2d(self, x: float, y: float) -> float:
        return self.base_noise.noise2d(x, y) * self.scale

      def fbm2d(self, x: float, y: float) -> float:
        return self.base_noise.fbm2d(x, y) * self.scale

      def noise_array2d(self, x_coords, y_coords):
        return self.base_noise.noise_array2d(x_coords, y_coords) * self.scale

      def fbm_array2d(self, x_coords, y_coords):
        return self.base_noise.fbm_array2d(x_coords, y_coords) * self.scale

      def generate_noise_map(
        self,
        width: int,
        height: int,
        x_offset: float = 0.0,
        y_offset: float = 0.0,
        use_fbm: bool = True,
      ):
        return (
          self.base_noise.generate_noise_map(width, height, x_offset, y_offset, use_fbm)
          * self.scale
        )

    return ScaledNoise(base_noise, amplitude)  # type: ignore

  @staticmethod
  def validate_notch_params(notch_size: float, notch_depth: float, notch_offset: float) -> None:
    """Validate notch parameters are within acceptable ranges.

    :param notch_size: Size of notch along edge axis (0.0-1.0)
    :param notch_depth: Depth of notch perpendicular to edge (0.0-1.0)
    :param notch_offset: Offset from center position (-0.5 to 0.5)
    :raises ValueError: If any parameter is outside valid range
    """
    GeoUtil.validate_dimension(notch_size, 'notch_size', 0.0, 1.0, exclusive_min=False)
    GeoUtil.validate_dimension(notch_depth, 'notch_depth', 0.0, 1.0, exclusive_min=False)
    GeoUtil.validate_dimension(notch_offset, 'notch_offset', -0.5, 0.5, exclusive_min=False)

  @staticmethod
  def calculate_notch_points(
    start: VectorPort,
    end: VectorPort,
    notch_size: float,
    notch_depth: float,
    notch_offset: float,
  ) -> list[VectorPort]:
    """Calculate points for a rectangular notch on an edge.

    Creates a rectangular indentation in the middle of the edge, with configurable
    size along the edge and depth perpendicular to it.

    :param start: Edge start point
    :param end: Edge end point
    :param notch_size: Size along edge (0.0-1.0, where 1.0 = full edge length)
    :param notch_depth: Depth perpendicular to edge (0.0-1.0, relative to edge length)
    :param notch_offset: Offset from center (-0.5 to 0.5, where 0.0 = centered)
    :returns: List of points forming the notch (empty if notch_size or notch_depth is 0.0)
    :raises ValueError: If parameters are outside valid ranges
    """
    # Validate parameters first
    GeoUtil.validate_notch_params(notch_size, notch_depth, notch_offset)

    # Return empty list if no notch needed
    if notch_size == 0.0 or notch_depth == 0.0:
      return []

    # Calculate edge vector and properties
    edge_x = end.x - start.x
    edge_y = end.y - start.y
    edge_length = math.sqrt(edge_x * edge_x + edge_y * edge_y)

    # Handle zero-length edge
    if edge_length < 1e-10:
      return []

    # Normalize edge vector
    edge_unit_x = edge_x / edge_length
    edge_unit_y = edge_y / edge_length

    # Calculate perpendicular vector (rotated 90 degrees clockwise for inward notch)
    perp_unit_x = edge_unit_y
    perp_unit_y = -edge_unit_x

    # Calculate notch depth (width calculation not needed for this method)
    notch_inward_depth = edge_length * notch_depth  # Physical depth perpendicular to edge

    # Calculate center position with offset
    center_offset = notch_offset * edge_length
    center_t = 0.5 + (center_offset / edge_length) if edge_length > 0 else 0.5

    # Clamp to prevent overflow beyond edge boundaries
    half_notch_t = (notch_size / 2.0) if edge_length > 0 else 0.0
    clamped_center_t = max(half_notch_t, min(1.0 - half_notch_t, center_t))

    # Calculate notch corner positions along the edge
    left_t = clamped_center_t - half_notch_t
    right_t = clamped_center_t + half_notch_t

    # Calculate points along the edge
    left_edge_x = start.x + left_t * edge_x
    left_edge_y = start.y + left_t * edge_y
    right_edge_x = start.x + right_t * edge_x
    right_edge_y = start.y + right_t * edge_y

    # Calculate inner notch points (perpendicular inward from edge)
    left_inner_x = left_edge_x + perp_unit_x * notch_inward_depth
    left_inner_y = left_edge_y + perp_unit_y * notch_inward_depth
    right_inner_x = right_edge_x + perp_unit_x * notch_inward_depth
    right_inner_y = right_edge_y + perp_unit_y * notch_inward_depth

    from .vector import Vector

    # Return notch points in clockwise order for proper polygon construction
    result = [
      Vector(x=left_edge_x, y=left_edge_y),  # Left edge point
      Vector(x=left_inner_x, y=left_inner_y),  # Left inner point
      Vector(x=right_inner_x, y=right_inner_y),  # Right inner point
      Vector(x=right_edge_x, y=right_edge_y),  # Right edge point
    ]
    return result

  @staticmethod
  def calculate_angled_notch_points(
    start: VectorPort,
    end: VectorPort,
    notch_size: float,
    notch_depth: float,
    notch_offset: float,
    edge_angle: float,
  ) -> list[VectorPort]:
    """Calculate points for a rectangular notch with angle-aware sides.

    This is the KEY FIX for trapezoid notch alignment. Instead of creating
    notch sides perpendicular to the edge, this method aligns the notch sides
    with the provided edge angle for proper geometric alignment.

    Args:
      start: Edge start point
      end: Edge end point
      notch_size: Size along edge (0.0-1.0, where 1.0 = full edge length)
      notch_depth: Depth perpendicular to edge (0.0-1.0, relative to edge length)
      notch_offset: Offset from center (-0.5 to 0.5, where 0.0 = centered)
      edge_angle: Angle of the edge in radians for notch side alignment

    Returns:
      List of points forming the notch (empty if notch_size or notch_depth is 0.0)

    Raises:
      ValueError: If parameters are outside valid ranges

    """
    # Validate parameters first
    GeoUtil.validate_notch_params(notch_size, notch_depth, notch_offset)

    # Return empty list if no notch needed
    if notch_size == 0.0 or notch_depth == 0.0:
      return []

    # Calculate edge vector and properties
    edge_x = end.x - start.x
    edge_y = end.y - start.y
    edge_length = math.sqrt(edge_x * edge_x + edge_y * edge_y)

    # Handle zero-length edge
    if edge_length < 1e-10:
      return []

    # Calculate notch side direction based on edge angle
    # For slanted edges like trapezoids, notch sides should align with the edge angle
    # Use the edge angle to determine the direction of notch sides
    notch_side_x = math.cos(edge_angle)
    notch_side_y = math.sin(edge_angle)

    # Calculate notch depth (width calculation not needed for this method)
    notch_inward_depth = edge_length * notch_depth  # Physical depth

    # Calculate center position with offset
    center_offset = notch_offset * edge_length
    center_t = 0.5 + (center_offset / edge_length) if edge_length > 0 else 0.5

    # Clamp to prevent overflow beyond edge boundaries
    half_notch_t = (notch_size / 2.0) if edge_length > 0 else 0.0
    clamped_center_t = max(half_notch_t, min(1.0 - half_notch_t, center_t))

    # Calculate notch corner positions along the edge
    left_t = clamped_center_t - half_notch_t
    right_t = clamped_center_t + half_notch_t

    # Calculate points along the edge
    left_edge_x = start.x + left_t * edge_x
    left_edge_y = start.y + left_t * edge_y
    right_edge_x = start.x + right_t * edge_x
    right_edge_y = start.y + right_t * edge_y

    # Calculate inner notch points using edge angle direction
    # Move inward along the angle-aligned direction
    left_inner_x = left_edge_x + notch_side_x * notch_inward_depth
    left_inner_y = left_edge_y + notch_side_y * notch_inward_depth
    right_inner_x = right_edge_x + notch_side_x * notch_inward_depth
    right_inner_y = right_edge_y + notch_side_y * notch_inward_depth

    from .vector import Vector

    # Return notch points in clockwise order for proper polygon construction
    result = [
      Vector(x=left_edge_x, y=left_edge_y),  # Left edge point
      Vector(x=left_inner_x, y=left_inner_y),  # Left inner point (angle-aligned)
      Vector(x=right_inner_x, y=right_inner_y),  # Right inner point (angle-aligned)
      Vector(x=right_edge_x, y=right_edge_y),  # Right edge point
    ]
    return result

  @staticmethod
  def create_torn_edge(
    start: VectorPort,
    end: VectorPort,
    noise: 'NoisePort',
    segments: int = 100,
    smoothing_factor: float = 0.1,
  ) -> list[VectorPort]:
    """Create a torn edge between two points using noise.

    Uses margin-based positioning - the caller is responsible for positioning
    the start/end points inward by the noise amplitude to ensure displacement
    stays within bounds naturally.

    :param start: Starting point (should be inset by amplitude for bounded edges)
    :param end: Ending point (should be inset by amplitude for bounded edges)
    :param noise: Noise provider for edge distortion
    :param segments: Number of segments in the torn edge
    :param smoothing_factor: Smoothing factor (0.0-1.0)
    :returns: List of points forming the torn edge
    """
    from .line import Line  # Import here to avoid circular dependency

    line = Line(
      start=start,
      stop=end,
      noise=noise,
      noise_segments=segments,
      smoothing_factor=smoothing_factor,
    )

    result = list(line.build_shape())
    return result
