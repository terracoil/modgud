"""Geometric utility functions and validators."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from ...domain.ports.vector_port import VectorPort
from .vector import Vector

if TYPE_CHECKING:
  from ...domain.ports.noise_port import NoisePort


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

  @staticmethod
  def validate_torn_sides(torn_sides: str) -> None:
    """
    Validate torn_sides parameter contains only valid side characters.

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
    """
    Get amplitude with proper sign for fitting constraints.

    North and South edges must have opposite tear directions for fitting.
    East and West edges must have opposite tear directions for fitting.

    :param base_amplitude: Base amplitude value
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
    """
    Create a noise instance with scaled amplitude.

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
  def create_torn_edge(
    start: VectorPort,
    end: VectorPort,
    noise: 'NoisePort',
    segments: int = 100,
    smoothing_factor: float = 0.1,
  ) -> list[VectorPort]:
    """
    Create a torn edge between two points using noise.

    :param start: Starting point
    :param end: Ending point
    :param noise: Noise provider for edge distortion
    :param segments: Number of segments in the torn edge
    :param smoothing_factor: Smoothing factor (0.0-1.0)
    :returns: List of points forming the torn edge
    """
    from .line import Line  # Import here to avoid circular dependency

    line = Line(
      start=start, stop=end, noise=noise, noise_segments=segments, smoothing_factor=smoothing_factor
    )

    result = list(line.build_shape())
    return result
