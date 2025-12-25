"""Torn paper shape generator with procedural torn edges."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from ...domain.ports.noise_port import NoisePort
from ...domain.ports.vector_port import VectorPort
from .line import Line
from .vector import Vector
from .vector_path import VectorPath


@dataclass(frozen=True)
class TornPaper:
  """Generate rectangles with procedurally torn edges using NoisePort for natural appearance."""

  noise: NoisePort
  torn_sides: str = 'NS'
  segments: int = 100
  amplitude: float = 5.0
  width: float = 100
  height: float = 100
  smoothing_factor: float = 0.1

  def __post_init__(self):
    """Validate parameters after initialization."""
    self._validate_parameters()

  def build_shape(self) -> Sequence[VectorPort]:
    """
    Calculate coordinates for torn paper with matching edges.

    Creates a rectangular paper shape with procedurally torn edges on specified sides.
    North↔South and East↔West edges use matching tear patterns for fitting.

    :returns: Sequence of VectorPort objects representing the paper outline
    """
    # Normalize torn_sides to uppercase
    torn_sides_upper = self.torn_sides.upper()

    # Create paper outline path
    paper_path = self._create_paper_outline(torn_sides_upper)

    # Return the absolute vector positions
    result = list(paper_path.gen_absolute_segments())

    return result

  def _validate_parameters(self) -> None:
    """Validate all input parameters."""
    # Validate torn_sides
    valid_sides = set('NSEW')
    torn_upper = self.torn_sides.upper()
    if not torn_upper or not all(s in valid_sides for s in torn_upper):
      raise ValueError("torn_sides must contain only 'N', 'S', 'E', 'W' characters")

    # Validate segments
    if self.segments < 10 or self.segments > 1000:
      raise ValueError('segments must be between 10 and 1000')

    # Validate amplitude
    if self.amplitude < 0.1 or self.amplitude > 50.0:
      raise ValueError('amplitude must be between 0.1 and 50.0')

    # Validate smoothing_factor
    if self.smoothing_factor < 0.0 or self.smoothing_factor > 1.0:
      raise ValueError('smoothing_factor must be between 0.0 and 1.0')

  def _create_paper_outline(self, torn_sides: str) -> VectorPath:
    """Create the complete paper outline with torn edges using Line class."""
    # Define paper corners in clockwise order
    corners = [
      Vector(0, 0, name='topLeft'),  # Top-left
      Vector(self.width, 0, name='topRight'),  # Top-right
      Vector(self.width, self.height, name='bottomRight'),  # Bottom-right
      Vector(0, self.height, name='bottomLeft'),  # Bottom-left
    ]

    # Collect all absolute positions for the path
    all_segments = []

    # Add edges in clockwise order using Line class
    edges = [
      ('N', corners[0], corners[1], 'top'),  # North: top-left to top-right
      ('E', corners[1], corners[2], 'right'),  # East: top-right to bottom-right
      ('S', corners[2], corners[3], 'bottom'),  # South: bottom-right to bottom-left
      ('W', corners[3], corners[0], 'left'),  # West: bottom-left to top-left
    ]

    for side, start_corner, end_corner, edge_name in edges:
      if side in torn_sides:
        # Create noisy line with adjusted amplitude
        adjusted_amplitude = self._get_fitting_amplitude(self.amplitude, side)

        # Create a modified noise instance with amplitude scaling
        scaled_noise = self._create_scaled_noise(adjusted_amplitude)

        line = Line(
          start=start_corner,
          stop=end_corner,
          noise=scaled_noise,
          noise_segments=self.segments,
          smoothing_factor=self.smoothing_factor,
        )

        # Get the torn edge segments (excluding start point to avoid duplication)
        edge_segments = line.build_shape()
        all_segments.extend(edge_segments[1:])  # Skip first point (start)
      else:
        # Straight edge - just add the end corner
        all_segments.append(end_corner.clone(name=f'{edge_name}End'))

    # Create path with absolute segments (will be converted to relative internally)
    paper_path = VectorPath(name='tornPaper', abs_segments=all_segments)

    return paper_path

  def _get_fitting_amplitude(self, base_amplitude: float, side: str) -> float:
    """Get amplitude with proper sign for fitting constraints."""
    # North and South edges must have opposite tear directions for fitting
    # East and West edges must have opposite tear directions for fitting
    fitting_signs = {
      'N': 1,  # North tears away from center
      'S': -1,  # South tears opposite to North
      'E': 1,  # East tears away from center
      'W': -1,  # West tears opposite to East
    }

    return base_amplitude * fitting_signs[side]

  def _create_scaled_noise(self, amplitude: float) -> NoisePort:
    """Create a noise instance with scaled amplitude."""

    # Create a wrapper that scales the noise output
    class ScaledNoise:
      def __init__(self, base_noise: NoisePort, scale: float):
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

    return ScaledNoise(self.noise, amplitude)  # type: ignore
