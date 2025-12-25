"""SimplexNoise Implementation with Fractal Brownian Motion support."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

import numpy as np

if TYPE_CHECKING:
  pass


@dataclass(frozen=True)
class SimplexNoise:
  """
  Simplex Noise implementation of the NoisePort.

  Implements Ken Perlin's simplex noise algorithm with fBm support.
  See NoisePort for detailed method documentation.

  :param seed: Random seed for reproducible noise patterns
  :param scale: Global scale multiplier for noise coordinates
  :param offset_x: X-axis offset for noise sampling
  :param offset_y: Y-axis offset for noise sampling
  :param octaves: Number of octaves for fractal Brownian motion
  :param persistence: Amplitude reduction factor between octaves (0.0-1.0)
  :param lacunarity: Frequency multiplier between octaves (typically 2.0)
  :param amplitude: Base amplitude scaling factor
  """

  seed: int = 0
  scale: float = 1.0
  offset_x: float = 0.0
  offset_y: float = 0.0
  octaves: int = 1
  persistence: float = 0.5
  lacunarity: float = 2.0
  amplitude: float = 1.0

  # Private attributes for permutation tables (set in __post_init__)
  _perm: np.ndarray = field(init=False)
  _perm_mod8: np.ndarray = field(init=False)

  # Constants for 2D simplex noise
  F2: ClassVar[float] = 0.36602540378  # (sqrt(3) - 1) / 2
  G2: ClassVar[float] = 0.21132486541  # (3 - sqrt(3)) / 6

  # Permutation table for gradient selection
  # fmt: off
  PERM: ClassVar[np.ndarray] = np.array(
    [151, 160, 137, 91, 90, 15, 131, 13, 201, 95, 96, 53, 194, 233, 7, 225, 140, 36, 103, 30, 69, 142, 8, 99, 37, 240,
     21, 10, 23, 190, 6, 148, 247, 120, 234, 75, 0, 26, 197, 62, 94, 252, 219, 203, 117, 35, 11, 32, 57, 177, 33, 88,
     237, 149, 56, 87, 174, 20, 125, 136, 171, 168, 68, 175, 74, 165, 71, 134, 139, 48, 27, 166, 77, 146, 158, 231, 83,
     111, 229, 122, 60, 211, 133, 230, 220, 105, 92, 41, 55, 46, 245, 40, 244, 102, 143, 54, 65, 25, 63, 161, 1, 216,
     80, 73, 209, 76, 132, 187, 208, 89, 18, 169, 200, 196, 135, 130, 116, 188, 159, 86, 164, 100, 109, 198, 173, 186,
     3, 64, 52, 217, 226, 250, 124, 123, 5, 202, 38, 147, 118, 126, 255, 82, 85, 212, 207, 206, 59, 227, 47, 16, 58, 17,
     182, 189, 28, 42, 223, 183, 170, 213, 119, 248, 152, 2, 44, 154, 163, 70, 221, 153, 101, 155, 167, 43, 172, 9, 129,
     22, 39, 253, 19, 98, 108, 110, 79, 113, 224, 232, 178, 185, 112, 104, 218, 246, 97, 228, 251, 34, 242, 193, 238,
     210, 144, 12, 191, 179, 162, 241, 81, 51, 145, 235, 249, 14, 239, 107, 49, 192, 214, 31, 181, 199, 106, 157, 184,
     84, 204, 176, 115, 121, 50, 45, 127, 4, 150, 254, 138, 236, 205, 93, 222, 114, 67, 29, 24, 72, 243, 141, 128, 195,
     78, 66, 215, 61, 156, 180, ], dtype=np.int32, )

  # Gradient vectors for 2D
  GRAD2: ClassVar[np.ndarray] = np.array([[1, 1], [-1, 1], [1, -1], [-1, -1], [1, 0], [-1, 0], [0, 1], [0, -1]], dtype=np.float32)
  # fmt: on

  def __post_init__(self) -> None:
    """Initialize permutation table with seed."""
    # Create seeded permutation table
    object.__setattr__(self, '_perm', self._create_permutation_table())
    object.__setattr__(self, '_perm_mod8', self._perm % 8)

  def _create_permutation_table(self) -> np.ndarray:
    """Create permutation table based on seed."""
    if self.seed == 0:
      # Use default permutation table doubled for wrapping
      return np.concatenate([self.PERM, self.PERM])

    # Create seeded permutation
    rng = np.random.RandomState(self.seed)
    perm = np.arange(256, dtype=np.int32)
    rng.shuffle(perm)
    return np.concatenate([perm, perm])

  def _fade(self, t: float) -> float:
    """Fade function for smooth interpolation: 6t^5 - 15t^4 + 10t^3."""
    return t * t * t * (t * (t * 6 - 15) + 10)

  def _grad2d(self, hash_value: int, x: float, y: float) -> float:
    """Calculate gradient contribution for 2D noise."""
    grad = self.GRAD2[hash_value]
    return grad[0] * x + grad[1] * y

  def noise2d(self, x: float, y: float) -> float:
    """Generate 2D simplex noise. See NoisePort.noise2d for details."""
    # Apply global transformations
    x = (x + self.offset_x) * self.scale
    y = (y + self.offset_y) * self.scale

    # Skew input space to determine which simplex cell we're in
    s = (x + y) * self.F2
    i = int(x + s)
    j = int(y + s)

    # Unskew cell origin back to (x, y) space
    t = (i + j) * self.G2
    x0 = x - (i - t)  # Distance from first vertex
    y0 = y - (j - t)

    # Determine which simplex we're in
    if x0 > y0:
      i1, j1 = 1, 0  # Lower triangle, (1,0) second vertex
    else:
      i1, j1 = 0, 1  # Upper triangle, (0,1) second vertex

    # Offsets for second vertex
    x1 = x0 - i1 + self.G2
    y1 = y0 - j1 + self.G2

    # Offsets for third vertex
    x2 = x0 - 1.0 + 2.0 * self.G2
    y2 = y0 - 1.0 + 2.0 * self.G2

    # Wrap indices for permutation table lookup
    ii = i & 255
    jj = j & 255

    # Calculate gradient contributions from each vertex
    gi0 = self._perm_mod8[ii + self._perm[jj]]
    gi1 = self._perm_mod8[ii + i1 + self._perm[jj + j1]]
    gi2 = self._perm_mod8[ii + 1 + self._perm[jj + 1]]

    # Calculate noise contributions from each vertex
    n0 = n1 = n2 = 0.0

    # First vertex contribution
    t0 = 0.5 - x0 * x0 - y0 * y0
    if t0 >= 0:
      t0 *= t0
      n0 = t0 * t0 * self._grad2d(gi0, x0, y0)

    # Second vertex contribution
    t1 = 0.5 - x1 * x1 - y1 * y1
    if t1 >= 0:
      t1 *= t1
      n1 = t1 * t1 * self._grad2d(gi1, x1, y1)

    # Third vertex contribution
    t2 = 0.5 - x2 * x2 - y2 * y2
    if t2 >= 0:
      t2 *= t2
      n2 = t2 * t2 * self._grad2d(gi2, x2, y2)

    # Scale and return final noise value
    return float(70.0 * (n0 + n1 + n2) * self.amplitude)

  def fbm2d(self, x: float, y: float) -> float:
    """Generate fBm noise using multiple octaves. See NoisePort.fbm2d for details."""
    if self.octaves <= 1:
      return self.noise2d(x, y)

    total = 0.0
    amplitude = self.amplitude
    frequency = 1.0
    max_value = 0.0

    for _ in range(self.octaves):
      # Create new instance with adjusted parameters for this octave
      octave_noise = SimplexNoise(
        seed=self.seed,
        scale=self.scale * frequency,
        offset_x=self.offset_x,
        offset_y=self.offset_y,
        octaves=1,
        persistence=self.persistence,
        lacunarity=self.lacunarity,
        amplitude=amplitude,
      )

      total += octave_noise.noise2d(x, y)
      max_value += amplitude

      # Prepare for next octave
      amplitude *= self.persistence
      frequency *= self.lacunarity

    # Normalize to maintain roughly the same range
    return total / max_value if max_value > 0 else 0.0

  def noise_array2d(self, x_coords: np.ndarray, y_coords: np.ndarray) -> np.ndarray:
    """Generate noise for coordinate arrays. See NoisePort.noise_array2d for details."""
    # Ensure inputs are numpy arrays
    x_coords = np.asarray(x_coords, dtype=np.float32)
    y_coords = np.asarray(y_coords, dtype=np.float32)

    # Handle empty arrays
    if x_coords.size == 0 or y_coords.size == 0:
      return np.array([], dtype=np.float32)

    # Vectorized noise generation
    result = np.zeros_like(x_coords, dtype=np.float32)
    flat_x = x_coords.flat
    flat_y = y_coords.flat
    flat_result = result.flat

    for i, (x_val, y_val) in enumerate(zip(flat_x, flat_y, strict=True)):
      flat_result[i] = self.noise2d(float(x_val), float(y_val))

    return result

  def fbm_array2d(self, x_coords: np.ndarray, y_coords: np.ndarray) -> np.ndarray:
    """Generate fBm for coordinate arrays. See NoisePort.fbm_array2d for details."""
    # Ensure inputs are numpy arrays
    x_coords = np.asarray(x_coords, dtype=np.float32)
    y_coords = np.asarray(y_coords, dtype=np.float32)

    # Handle empty arrays
    if x_coords.size == 0 or y_coords.size == 0:
      return np.array([], dtype=np.float32)

    # Vectorized fBm generation
    result = np.zeros_like(x_coords, dtype=np.float32)
    flat_x = x_coords.flat
    flat_y = y_coords.flat
    flat_result = result.flat

    for i, (x_val, y_val) in enumerate(zip(flat_x, flat_y, strict=True)):
      flat_result[i] = self.fbm2d(float(x_val), float(y_val))

    return result

  def generate_noise_map(
    self,
    width: int,
    height: int,
    x_offset: float = 0.0,
    y_offset: float = 0.0,
    use_fbm: bool = True,
  ) -> np.ndarray:
    """Generate 2D noise map. See NoisePort.generate_noise_map for details."""
    # Create coordinate grids
    x_coords = np.linspace(x_offset, x_offset + width / self.scale, width)
    y_coords = np.linspace(y_offset, y_offset + height / self.scale, height)
    x_grid, y_grid = np.meshgrid(x_coords, y_coords, indexing='xy')

    # Generate noise values
    if use_fbm and self.octaves > 1:
      return self.fbm_array2d(x_grid, y_grid)
    return self.noise_array2d(x_grid, y_grid)

  def with_seed(self, seed: int) -> SimplexNoise:
    """
    Create new SimplexNoise instance with different seed.

    SimplexNoise-specific builder method for creating variations.
    Preserves all other parameters while changing the seed.

    :param seed: New random seed for noise generation
    :returns: New SimplexNoise instance with updated seed
    """
    return SimplexNoise(
      seed=seed,
      scale=self.scale,
      offset_x=self.offset_x,
      offset_y=self.offset_y,
      octaves=self.octaves,
      persistence=self.persistence,
      lacunarity=self.lacunarity,
      amplitude=self.amplitude,
    )

  def with_octaves(
    self, octaves: int, persistence: float | None = None, lacunarity: float | None = None
  ) -> SimplexNoise:
    """
    Create new SimplexNoise instance with different fractal parameters.

    SimplexNoise-specific builder method for adjusting fBm characteristics.
    Allows fine-tuning the fractal noise behavior.

    :param octaves: Number of noise layers to combine
    :param persistence: Amplitude decay between octaves (default: keep current)
    :param lacunarity: Frequency multiplier between octaves (default: keep current)
    :returns: New SimplexNoise instance with updated fractal parameters
    """
    return SimplexNoise(
      seed=self.seed,
      scale=self.scale,
      offset_x=self.offset_x,
      offset_y=self.offset_y,
      octaves=octaves,
      persistence=persistence if persistence is not None else self.persistence,
      lacunarity=lacunarity if lacunarity is not None else self.lacunarity,
      amplitude=self.amplitude,
    )

  def with_scale(self, scale: float) -> SimplexNoise:
    """
    Create new SimplexNoise instance with different scale.

    SimplexNoise-specific builder method for adjusting noise frequency.
    Larger scales produce smoother, lower-frequency noise.

    :param scale: New scale factor for noise coordinates
    :returns: New SimplexNoise instance with updated scale
    """
    return SimplexNoise(
      seed=self.seed,
      scale=scale,
      offset_x=self.offset_x,
      offset_y=self.offset_y,
      octaves=self.octaves,
      persistence=self.persistence,
      lacunarity=self.lacunarity,
      amplitude=self.amplitude,
    )

  def with_offset(self, offset_x: float, offset_y: float) -> SimplexNoise:
    """
    Create new SimplexNoise instance with different offset.

    SimplexNoise-specific builder method for sampling different regions
    of the infinite noise field.

    :param offset_x: New X-axis offset in noise space
    :param offset_y: New Y-axis offset in noise space
    :returns: New SimplexNoise instance with updated offsets
    """
    return SimplexNoise(
      seed=self.seed,
      scale=self.scale,
      offset_x=offset_x,
      offset_y=offset_y,
      octaves=self.octaves,
      persistence=self.persistence,
      lacunarity=self.lacunarity,
      amplitude=self.amplitude,
    )
