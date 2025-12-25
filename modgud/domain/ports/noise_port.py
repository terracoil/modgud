"""Protocol for noise generation implementations."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import numpy as np


@runtime_checkable
class NoisePort(Protocol):
  """
  Protocol defining the interface for noise generators.

  This protocol establishes a common interface for various noise generation
  algorithms (Simplex, Perlin, Worley, etc.) with support for both single-point
  and array-based noise generation, as well as fractal Brownian motion (fBm).

  Implementing classes should provide efficient noise generation with:
  - Deterministic output based on seed values
  - Smooth gradients suitable for procedural generation
  - Support for both single-value and bulk array operations
  - Optional fractal layering through fBm
  """

  def noise2d(self, x: float, y: float) -> float:
    """
    Generate 2D noise value at given coordinates.

    This is the core noise generation method that produces a smooth,
    continuous noise value for any given 2D coordinate. The noise
    should be deterministic (same input always produces same output)
    and have good spatial coherence (nearby points have similar values).

    :param x: X coordinate in noise space
    :param y: Y coordinate in noise space
    :returns: Noise value, typically normalized between -1.0 and 1.0
    """
    ...

  def fbm2d(self, x: float, y: float) -> float:
    """
    Generate fractal Brownian motion (fBm) noise at given coordinates.

    Fractal Brownian motion combines multiple octaves of noise at
    different frequencies and amplitudes to create more complex,
    natural-looking patterns. Each octave typically has:
    - Double the frequency (controlled by lacunarity)
    - Reduced amplitude (controlled by persistence)

    The result is noise with both large-scale structure and fine detail,
    suitable for terrain generation, clouds, and other natural phenomena.

    :param x: X coordinate in noise space
    :param y: Y coordinate in noise space
    :returns: fBm noise value combining multiple octaves
    """
    ...

  def noise_array2d(self, x_coords: np.ndarray, y_coords: np.ndarray) -> np.ndarray:
    """
    Generate 2D noise values for arrays of coordinates.

    Efficient bulk generation of noise values for multiple coordinate
    pairs. This method should handle coordinate arrays of any shape,
    returning a result array of the same shape containing the
    corresponding noise values.

    Implementations should optimize for vectorized operations where
    possible to improve performance over individual noise2d calls.

    :param x_coords: Array of X coordinates
    :param y_coords: Array of Y coordinates (must match shape of x_coords)
    :returns: Array of noise values with same shape as input arrays
    :raises ValueError: If x_coords and y_coords have different shapes
    """
    ...

  def fbm_array2d(self, x_coords: np.ndarray, y_coords: np.ndarray) -> np.ndarray:
    """
    Generate fractal Brownian motion values for arrays of coordinates.

    Bulk generation of fBm noise values, combining the efficiency of
    array processing with the complexity of fractal noise. This method
    should produce the same results as calling fbm2d for each coordinate
    pair, but with better performance for large datasets.

    :param x_coords: Array of X coordinates
    :param y_coords: Array of Y coordinates (must match shape of x_coords)
    :returns: Array of fBm noise values with same shape as input arrays
    :raises ValueError: If x_coords and y_coords have different shapes
    """
    ...

  def generate_noise_map(
    self,
    width: int,
    height: int,
    x_offset: float = 0.0,
    y_offset: float = 0.0,
    use_fbm: bool = True,
  ) -> np.ndarray:
    """
    Generate a 2D noise map of specified dimensions.

    Creates a complete 2D array of noise values suitable for use as
    heightmaps, textures, or other 2D data. The map covers a rectangular
    region in noise space, with optional offset for sampling different
    areas of the infinite noise field.

    The method should handle:
    - Automatic coordinate generation based on dimensions
    - Proper scaling to maintain consistent noise frequency
    - Optional fBm for more detailed output
    - Efficient memory usage for large maps

    :param width: Width of the noise map in pixels
    :param height: Height of the noise map in pixels
    :param x_offset: Starting X coordinate in noise space
    :param y_offset: Starting Y coordinate in noise space
    :param use_fbm: Whether to use fractal Brownian motion for richer detail
    :returns: 2D numpy array of shape (height, width) containing noise values
    :raises ValueError: If width or height are non-positive
    """
    ...
