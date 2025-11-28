"""Test that SimplexNoise properly implements NoisePort."""

import numpy as np
from modgud.util.geo import NoisePort, SimplexNoise


def test_simplex_noise_implements_protocol():
  """Verify SimplexNoise implements NoisePort interface."""
  noise = SimplexNoise(seed=42, scale=0.1)

  # Runtime check that SimplexNoise implements NoisePort
  assert isinstance(noise, NoisePort)


def test_protocol_methods_exist():
  """Verify all protocol methods are implemented."""
  noise = SimplexNoise()

  # Check all required methods exist
  assert hasattr(noise, 'noise2d')
  assert hasattr(noise, 'fbm2d')
  assert hasattr(noise, 'noise_array2d')
  assert hasattr(noise, 'fbm_array2d')
  assert hasattr(noise, 'generate_noise_map')

  # Check they're callable
  assert callable(noise.noise2d)
  assert callable(noise.fbm2d)
  assert callable(noise.noise_array2d)
  assert callable(noise.fbm_array2d)
  assert callable(noise.generate_noise_map)


def test_noise2d_basic():
  """Test basic 2D noise generation."""
  noise = SimplexNoise(seed=42)

  # Test single point
  value = noise.noise2d(0.5, 0.5)
  assert isinstance(value, float)
  assert -1.0 <= value <= 1.0

  # Test deterministic output
  value2 = noise.noise2d(0.5, 0.5)
  assert value == value2


def test_fbm2d_basic():
  """Test fractal Brownian motion."""
  noise = SimplexNoise(seed=42, octaves=4)

  # Test single point
  value = noise.fbm2d(0.5, 0.5)
  assert isinstance(value, float)

  # Should be different from basic noise due to octaves
  basic_value = noise.noise2d(0.5, 0.5)
  assert value != basic_value


def test_noise_arrays():
  """Test array-based noise generation."""
  noise = SimplexNoise(seed=42)

  # Create test arrays
  x_coords = np.array([0.0, 0.5, 1.0])
  y_coords = np.array([0.0, 0.5, 1.0])

  # Test noise array
  result = noise.noise_array2d(x_coords, y_coords)
  assert isinstance(result, np.ndarray)
  assert result.shape == x_coords.shape
  assert all(-1.0 <= v <= 1.0 for v in result.flat)

  # Test fBm array
  fbm_result = noise.fbm_array2d(x_coords, y_coords)
  assert isinstance(fbm_result, np.ndarray)
  assert fbm_result.shape == x_coords.shape


def test_generate_noise_map():
  """Test noise map generation."""
  # Use multiple octaves so fbm is different from basic noise
  noise = SimplexNoise(seed=42, scale=0.1, octaves=4)

  # Generate basic noise map
  noise_map = noise.generate_noise_map(10, 10, use_fbm=False)
  assert isinstance(noise_map, np.ndarray)
  assert noise_map.shape == (10, 10)

  # Generate fBm noise map
  fbm_map = noise.generate_noise_map(10, 10, use_fbm=True)
  assert isinstance(fbm_map, np.ndarray)
  assert fbm_map.shape == (10, 10)

  # With multiple octaves, maps should be different
  assert not np.array_equal(noise_map, fbm_map)
