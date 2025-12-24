"""Torn paper shape generator with procedural torn edges."""

from __future__ import annotations

import math
from typing import Literal

from .simplex_noise import SimplexNoise
from .vector import Vector
from .vector_path import VectorPath


class TornPaper:
  """Generate rectangles with procedurally torn edges using SimplexNoise for natural appearance."""

  def __init__(self, seed: int = 42):
    """
    Initialize torn paper generator.

    :param seed: Random seed for reproducible tear patterns
    """
    self.seed = seed

  def calculate_torn_paper(
    self,
    torn_sides: str = 'NS',
    segments: int = 100,
    amplitude: float = 5.0,
    width: float = 100,
    height: float = 100,
    noise_scale: float = 0.1,
    octaves: int = 3,
  ) -> dict[str, list[str]]:
    """
    Calculate coordinates for torn paper with matching edges.

    Creates a rectangular paper shape with procedurally torn edges on specified sides.
    North↔South and East↔West edges use matching tear patterns for fitting.

    :param torn_sides: Sides to tear ('N', 'S', 'E', 'W' combinations, case-insensitive)
    :param segments: Number of segments per torn edge (10-1000)
    :param amplitude: Maximum tear deviation in units (0.1-50.0)
    :param width: Paper width in units
    :param height: Paper height in units
    :param noise_scale: SimplexNoise scale factor for tear frequency (0.01-1.0)
    :param octaves: Number of noise octaves for tear complexity (1-6)
    :returns: Dictionary with 'shape' SVG path array
    :raises ValueError: For invalid parameter values
    """
    # Validate parameters
    self._validate_parameters(torn_sides, segments, amplitude, noise_scale, octaves)

    # Normalize torn_sides to uppercase
    torn_sides = torn_sides.upper()

    # Create paper outline path
    paper_path = self._create_paper_outline(
      torn_sides, segments, amplitude, width, height, noise_scale, octaves
    )

    # Generate SVG output
    result = {'shape': list(paper_path.svg_path())}

    return result

  def _validate_parameters(
    self,
    torn_sides: str,
    segments: int,
    amplitude: float,
    noise_scale: float,
    octaves: int,
  ) -> None:
    """Validate all input parameters."""
    # Validate torn_sides
    valid_sides = set('NSEW')
    torn_upper = torn_sides.upper()
    if not torn_upper or not all(s in valid_sides for s in torn_upper):
      raise ValueError("torn_sides must contain only 'N', 'S', 'E', 'W' characters")

    # Validate segments
    if segments < 10 or segments > 1000:
      raise ValueError('segments must be between 10 and 1000')

    # Validate amplitude
    if amplitude < 0.1 or amplitude > 50.0:
      raise ValueError('amplitude must be between 0.1 and 50.0')

    # Validate noise_scale
    if noise_scale < 0.01 or noise_scale > 1.0:
      raise ValueError('noise_scale must be between 0.01 and 1.0')

    # Validate octaves
    if octaves < 1 or octaves > 6:
      raise ValueError('octaves must be between 1 and 6')

  def _create_paper_outline(
    self,
    torn_sides: str,
    segments: int,
    amplitude: float,
    width: float,
    height: float,
    noise_scale: float,
    octaves: int,
  ) -> VectorPath:
    """Create the complete paper outline with torn edges."""
    # Define paper corners in clockwise order
    corners = [
      Vector(0, 0, name='topLeft'),      # Top-left
      Vector(width, 0, name='topRight'),    # Top-right
      Vector(width, height, name='bottomRight'), # Bottom-right
      Vector(0, height, name='bottomLeft'),     # Bottom-left
    ]

    # Create path starting from top-left
    paper_path = VectorPath(name='tornPaper')

    # Add edges in clockwise order
    edges = [
      ('N', corners[0], corners[1], 'top'),     # North: top-left to top-right
      ('E', corners[1], corners[2], 'right'),   # East: top-right to bottom-right
      ('S', corners[2], corners[3], 'bottom'),  # South: bottom-right to bottom-left
      ('W', corners[3], corners[0], 'left'),    # West: bottom-left to top-left
    ]

    for side, start_corner, end_corner, edge_name in edges:
      if side in torn_sides:
        edge_segments = self._create_torn_edge(
          start_corner, end_corner, segments, amplitude, noise_scale, octaves, side
        )
      else:
        edge_segments = [end_corner.clone(name=f'{edge_name}End')]

      # Add segments to path
      for segment in edge_segments:
        paper_path.push_segment(segment)

    return paper_path

  def _create_torn_edge(
    self,
    start: Vector,
    end: Vector,
    segments: int,
    amplitude: float,
    noise_scale: float,
    octaves: int,
    side: str,
  ) -> list[Vector]:
    """Generate torn edge using SimplexNoise with fitting constraints."""
    # Create noise generator with fitting parameters
    noise = SimplexNoise(
      seed=self.seed,
      scale=noise_scale,
      octaves=octaves,
      persistence=0.5,
      lacunarity=2.0,
    )

    # Calculate edge direction and perpendicular
    edge_vector = end - start
    edge_length = math.sqrt(edge_vector.x**2 + edge_vector.y**2)

    # Get perpendicular vector for tear offset (pointing outward from shape)
    perpendicular = self._get_outward_perpendicular(edge_vector, side)

    # Determine amplitude direction for fitting constraints
    tear_amplitude = self._get_fitting_amplitude(amplitude, side)

    edge_segments = []

    # Generate segments along the edge
    for i in range(1, segments + 1):  # Skip start point (already in path)
      t = i / segments

      # Linear interpolation along edge
      interpolated_vector = Vector(edge_vector.x * t, edge_vector.y * t)
      base_pos = start + interpolated_vector

      # Generate noise offset perpendicular to edge
      # Use edge position along length for noise sampling
      noise_input = t * edge_length * 0.01  # Scale for reasonable noise frequency
      noise_value = noise.fbm2d(noise_input, float(side in 'NS'))

      # Apply amplitude with fitting direction
      offset_magnitude = noise_value * tear_amplitude
      tear_offset = Vector(
        perpendicular.x * offset_magnitude,
        perpendicular.y * offset_magnitude
      )
      torn_pos = base_pos + tear_offset

      # Name segments for debugging
      segment_name = f'{side.lower()}Edge-{i}'
      edge_segments.append(Vector(torn_pos.x, torn_pos.y, name=segment_name))

    return edge_segments

  def _get_outward_perpendicular(self, edge_vector: Vector, side: str) -> Vector:
    """Get perpendicular vector pointing outward from the paper shape."""
    # Rotate edge vector 90 degrees and normalize
    perp_x = -edge_vector.y
    perp_y = edge_vector.x
    perp_length = math.sqrt(perp_x**2 + perp_y**2)

    if perp_length == 0:
      return Vector(0, 0)

    # Normalize and apply direction multiplier
    # Adjust direction based on side to point outward
    outward_multipliers = {
      'N': -1,  # North edge tears upward (negative Y)
      'E': 1,   # East edge tears rightward (positive X)
      'S': 1,   # South edge tears downward (positive Y)
      'W': -1,  # West edge tears leftward (negative X)
    }

    multiplier = outward_multipliers[side]
    normalized_x = (perp_x / perp_length) * multiplier
    normalized_y = (perp_y / perp_length) * multiplier

    return Vector(normalized_x, normalized_y)

  def _get_fitting_amplitude(self, base_amplitude: float, side: str) -> float:
    """Get amplitude with proper sign for fitting constraints."""
    # North and South edges must have opposite tear directions for fitting
    # East and West edges must have opposite tear directions for fitting
    fitting_signs = {
      'N': 1,   # North tears away from center
      'S': -1,  # South tears opposite to North
      'E': 1,   # East tears away from center
      'W': -1,  # West tears opposite to East
    }

    return base_amplitude * fitting_signs[side]