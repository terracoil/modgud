"""Tests for SimplexNoise class."""

import numpy as np
import pytest
from modgud.util.geo import SimplexNoise


class TestSimplexNoiseCore:
  """Test core SimplexNoise functionality."""

  def test_default_initialization(self):
    """Test default SimplexNoise initialization."""
    noise = SimplexNoise()

    assert noise.seed == 0
    assert noise.scale == 1.0
    assert noise.offset_x == 0.0
    assert noise.offset_y == 0.0
    assert noise.octaves == 1
    assert noise.persistence == 0.5
    assert noise.lacunarity == 2.0
    assert noise.amplitude == 1.0

  def test_custom_initialization(self):
    """Test SimplexNoise with custom parameters."""
    noise = SimplexNoise(
      seed=42,
      scale=2.0,
      offset_x=10.0,
      offset_y=20.0,
      octaves=4,
      persistence=0.6,
      lacunarity=2.5,
      amplitude=0.8,
    )

    assert noise.seed == 42
    assert noise.scale == 2.0
    assert noise.offset_x == 10.0
    assert noise.offset_y == 20.0
    assert noise.octaves == 4
    assert noise.persistence == 0.6
    assert noise.lacunarity == 2.5
    assert noise.amplitude == 0.8

  def test_immutability(self):
    """Test that SimplexNoise instances are immutable."""
    noise = SimplexNoise()

    # Verify that attributes on frozen dataclass cannot be changed directly:
    with pytest.raises(AttributeError):
      noise.seed = 42

    with pytest.raises(AttributeError):
      noise.scale = 2.0


class TestSimplexNoise2D:
  """Test 2D noise generation."""

  def test_noise2d_basic(self):
    """Test basic 2D noise generation."""
    noise = SimplexNoise()

    # Test that noise generates values
    value = noise.noise2d(0.0, 0.0)
    assert isinstance(value, float)

    # Test that different coordinates produce different values
    value1 = noise.noise2d(1.0, 1.0)
    value2 = noise.noise2d(2.0, 2.0)
    assert value1 != value2

  def test_noise2d_deterministic(self):
    """Test that noise is deterministic for same coordinates."""
    noise = SimplexNoise(seed=42)

    value1 = noise.noise2d(1.5, 2.5)
    value2 = noise.noise2d(1.5, 2.5)

    assert value1 == value2

  def test_noise2d_seed_variation(self):
    """Test that different seeds produce different noise."""
    noise1 = SimplexNoise(seed=1)
    noise2 = SimplexNoise(seed=2)

    value1 = noise1.noise2d(1.0, 1.0)
    value2 = noise2.noise2d(1.0, 1.0)

    assert value1 != value2

  def test_noise2d_scale_effect(self):
    """Test that scale affects noise sampling."""
    noise1 = SimplexNoise(scale=1.0)
    noise2 = SimplexNoise(scale=0.5)

    # Scaling should change the noise pattern
    value1 = noise1.noise2d(2.0, 2.0)
    value2 = noise2.noise2d(2.0, 2.0)

    assert value1 != value2

  def test_noise2d_offset_effect(self):
    """Test that offset affects noise sampling."""
    noise1 = SimplexNoise(offset_x=0.0, offset_y=0.0)
    noise2 = SimplexNoise(offset_x=10.0, offset_y=5.0)

    value1 = noise1.noise2d(0.0, 0.0)
    value2 = noise2.noise2d(0.0, 0.0)

    assert value1 != value2

  def test_noise2d_amplitude_scaling(self):
    """Test that amplitude scales noise values."""
    noise1 = SimplexNoise(amplitude=1.0)
    noise2 = SimplexNoise(amplitude=2.0)

    value1 = noise1.noise2d(1.0, 1.0)
    value2 = noise2.noise2d(1.0, 1.0)

    # Value2 should be approximately twice value1
    assert abs(value2 - 2.0 * value1) < 0.01


class TestFractalBrownianMotion:
  """Test fractal Brownian motion functionality."""

  def test_fbm2d_single_octave(self):
    """Test fBm with single octave equals regular noise."""
    noise = SimplexNoise(octaves=1)

    regular_value = noise.noise2d(1.0, 1.0)
    fbm_value = noise.fbm2d(1.0, 1.0)

    assert regular_value == fbm_value

  def test_fbm2d_multiple_octaves(self):
    """Test fBm with multiple octaves."""
    noise = SimplexNoise(octaves=4, persistence=0.5, lacunarity=2.0)

    value = noise.fbm2d(1.0, 1.0)
    assert isinstance(value, float)

  def test_fbm2d_deterministic(self):
    """Test that fBm is deterministic."""
    noise = SimplexNoise(seed=42, octaves=3)

    value1 = noise.fbm2d(2.5, 3.5)
    value2 = noise.fbm2d(2.5, 3.5)

    assert value1 == value2

  def test_fbm2d_octave_effect(self):
    """Test that more octaves create different patterns."""
    noise1 = SimplexNoise(octaves=1, seed=42)
    noise2 = SimplexNoise(octaves=4, seed=42)

    value1 = noise1.fbm2d(1.0, 1.0)
    value2 = noise2.fbm2d(1.0, 1.0)

    assert value1 != value2

  def test_fbm2d_persistence_effect(self):
    """Test that persistence affects fBm output."""
    noise1 = SimplexNoise(octaves=3, persistence=0.3, seed=42)
    noise2 = SimplexNoise(octaves=3, persistence=0.7, seed=42)

    value1 = noise1.fbm2d(1.0, 1.0)
    value2 = noise2.fbm2d(1.0, 1.0)

    assert value1 != value2

  def test_fbm2d_lacunarity_effect(self):
    """Test that lacunarity affects fBm output."""
    noise1 = SimplexNoise(octaves=3, lacunarity=2.0, seed=42)
    noise2 = SimplexNoise(octaves=3, lacunarity=3.0, seed=42)

    value1 = noise1.fbm2d(1.0, 1.0)
    value2 = noise2.fbm2d(1.0, 1.0)

    assert value1 != value2


class TestArrayOperations:
  """Test numpy array-based noise generation."""

  def test_noise_array2d_basic(self):
    """Test basic array noise generation."""
    noise = SimplexNoise()

    x_coords = np.array([0.0, 1.0, 2.0])
    y_coords = np.array([0.0, 1.0, 2.0])

    result = noise.noise_array2d(x_coords, y_coords)

    assert isinstance(result, np.ndarray)
    assert result.shape == x_coords.shape
    assert result.dtype == np.float32

  def test_noise_array2d_2d_input(self):
    """Test array noise with 2D coordinate arrays."""
    noise = SimplexNoise()

    x_coords = np.array([[0.0, 1.0], [2.0, 3.0]])
    y_coords = np.array([[0.0, 1.0], [2.0, 3.0]])

    result = noise.noise_array2d(x_coords, y_coords)

    assert result.shape == (2, 2)
    assert isinstance(result[0, 0], np.floating)

  def test_fbm_array2d_basic(self):
    """Test basic array fBm generation."""
    noise = SimplexNoise(octaves=3)

    x_coords = np.array([0.0, 1.0, 2.0])
    y_coords = np.array([0.0, 1.0, 2.0])

    result = noise.fbm_array2d(x_coords, y_coords)

    assert isinstance(result, np.ndarray)
    assert result.shape == x_coords.shape
    assert result.dtype == np.float32

  def test_fbm_array2d_matches_individual_calls(self):
    """Test that array fBm matches individual calls."""
    noise = SimplexNoise(octaves=2, seed=42)

    x_coords = np.array([1.0, 2.0])
    y_coords = np.array([1.0, 2.0])

    array_result = noise.fbm_array2d(x_coords, y_coords)
    individual_results = [noise.fbm2d(1.0, 1.0), noise.fbm2d(2.0, 2.0)]

    np.testing.assert_allclose(array_result, individual_results, rtol=1e-6)


class TestNoiseMap:
  """Test noise map generation."""

  def test_generate_noise_map_basic(self):
    """Test basic noise map generation."""
    noise = SimplexNoise()

    noise_map = noise.generate_noise_map(10, 10)

    assert isinstance(noise_map, np.ndarray)
    assert noise_map.shape == (10, 10)

  def test_generate_noise_map_with_fbm(self):
    """Test noise map with fractal Brownian motion."""
    noise = SimplexNoise(octaves=3)

    noise_map = noise.generate_noise_map(5, 5, use_fbm=True)

    assert noise_map.shape == (5, 5)

  def test_generate_noise_map_no_fbm(self):
    """Test noise map without fBm."""
    noise = SimplexNoise(octaves=3)

    noise_map = noise.generate_noise_map(5, 5, use_fbm=False)

    assert noise_map.shape == (5, 5)

  def test_generate_noise_map_with_offsets(self):
    """Test noise map with coordinate offsets."""
    noise = SimplexNoise()

    map1 = noise.generate_noise_map(5, 5, x_offset=0.0, y_offset=0.0)
    map2 = noise.generate_noise_map(5, 5, x_offset=10.0, y_offset=10.0)

    # Maps should be different due to offset
    assert not np.allclose(map1, map2)

  def test_generate_noise_map_deterministic(self):
    """Test that noise maps are deterministic."""
    noise = SimplexNoise(seed=42)

    map1 = noise.generate_noise_map(3, 3)
    map2 = noise.generate_noise_map(3, 3)

    np.testing.assert_array_equal(map1, map2)


class TestBuilderMethods:
  """Test fluent builder-style methods."""

  def test_with_seed(self):
    """Test with_seed builder method."""
    original = SimplexNoise(seed=1)
    new_noise = original.with_seed(42)

    assert original.seed == 1
    assert new_noise.seed == 42
    assert new_noise.scale == original.scale
    assert new_noise.octaves == original.octaves

  def test_with_octaves(self):
    """Test with_octaves builder method."""
    original = SimplexNoise(octaves=1)
    new_noise = original.with_octaves(4, persistence=0.6, lacunarity=2.5)

    assert original.octaves == 1
    assert new_noise.octaves == 4
    assert new_noise.persistence == 0.6
    assert new_noise.lacunarity == 2.5
    assert new_noise.seed == original.seed

  def test_with_octaves_partial(self):
    """Test with_octaves with partial parameters."""
    original = SimplexNoise(persistence=0.5, lacunarity=2.0)
    new_noise = original.with_octaves(3)

    assert new_noise.octaves == 3
    assert new_noise.persistence == 0.5  # Preserved
    assert new_noise.lacunarity == 2.0  # Preserved

  def test_with_scale(self):
    """Test with_scale builder method."""
    original = SimplexNoise(scale=1.0)
    new_noise = original.with_scale(2.5)

    assert original.scale == 1.0
    assert new_noise.scale == 2.5
    assert new_noise.seed == original.seed

  def test_with_offset(self):
    """Test with_offset builder method."""
    original = SimplexNoise(offset_x=0.0, offset_y=0.0)
    new_noise = original.with_offset(10.0, 20.0)

    assert original.offset_x == 0.0
    assert original.offset_y == 0.0
    assert new_noise.offset_x == 10.0
    assert new_noise.offset_y == 20.0
    assert new_noise.seed == original.seed


class TestEdgeCases:
  """Test edge cases and error conditions."""

  def test_zero_octaves(self):
    """Test behavior with zero octaves."""
    noise = SimplexNoise(octaves=0)

    # Should fall back to single octave behavior
    value = noise.fbm2d(1.0, 1.0)
    expected = noise.noise2d(1.0, 1.0)
    assert value == expected

  def test_negative_coordinates(self):
    """Test noise with negative coordinates."""
    noise = SimplexNoise()

    value = noise.noise2d(-5.0, -10.0)
    assert isinstance(value, float)

  def test_large_coordinates(self):
    """Test noise with very large coordinates."""
    noise = SimplexNoise()

    value = noise.noise2d(1000.0, 2000.0)
    assert isinstance(value, float)

  def test_zero_scale(self):
    """Test behavior with zero scale."""
    noise = SimplexNoise(scale=0.0)

    # Should still generate noise (coordinates become 0 after scaling)
    value = noise.noise2d(100.0, 200.0)
    assert isinstance(value, float)

  def test_extreme_persistence(self):
    """Test fBm with extreme persistence values."""
    # Very low persistence
    noise1 = SimplexNoise(octaves=3, persistence=0.01)
    value1 = noise1.fbm2d(1.0, 1.0)
    assert isinstance(value1, float)

    # Very high persistence (close to 1)
    noise2 = SimplexNoise(octaves=3, persistence=0.99)
    value2 = noise2.fbm2d(1.0, 1.0)
    assert isinstance(value2, float)

  def test_empty_array_input(self):
    """Test noise generation with empty arrays."""
    noise = SimplexNoise()

    empty_x = np.array([])
    empty_y = np.array([])

    result = noise.noise_array2d(empty_x, empty_y)
    assert result.shape == (0,)

  def test_single_element_array(self):
    """Test noise generation with single-element arrays."""
    noise = SimplexNoise()

    x = np.array([1.5])
    y = np.array([2.5])

    result = noise.noise_array2d(x, y)
    expected = noise.noise2d(1.5, 2.5)

    assert result.shape == (1,)
    assert abs(result[0] - expected) < 1e-6


class TestNoiseProperties:
  """Test mathematical properties of the noise."""

  def test_noise_continuity(self):
    """Test that noise is reasonably continuous."""
    noise = SimplexNoise()

    # Sample nearby points
    x, y = 5.0, 3.0
    delta = 0.01

    center = noise.noise2d(x, y)
    neighbors = [
      noise.noise2d(x + delta, y),
      noise.noise2d(x - delta, y),
      noise.noise2d(x, y + delta),
      noise.noise2d(x, y - delta),
    ]

    # All neighbors should be reasonably close to center
    for neighbor in neighbors:
      difference = abs(neighbor - center)
      assert difference < 2.0  # Reasonable continuity bound

  def test_noise_range_bounds(self):
    """Test that noise values stay within reasonable bounds."""
    noise = SimplexNoise(amplitude=1.0)

    # Test many random points
    np.random.seed(42)
    test_points = np.random.uniform(-100, 100, (100, 2))

    for x, y in test_points:
      value = noise.noise2d(x, y)
      # Simplex noise should roughly stay within [-amplitude, amplitude]
      # Allow some tolerance for the scaling factor
      assert abs(value) <= 2.0 * noise.amplitude

  def test_fbm_octave_contribution(self):
    """Test that each octave contributes to fBm."""
    base_noise = SimplexNoise(octaves=1, seed=42)
    multi_octave = SimplexNoise(octaves=4, seed=42, persistence=0.5)

    base_value = base_noise.fbm2d(1.0, 1.0)
    multi_value = multi_octave.fbm2d(1.0, 1.0)

    # Multi-octave should produce different (usually more detailed) result
    assert base_value != multi_value
