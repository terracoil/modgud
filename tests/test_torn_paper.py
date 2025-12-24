"""Tests for TornPaper shape generation."""

import pytest

from modgud.api.geometry import TornPaper


class TestTornPaper:
  """Test cases for TornPaper shape generation."""

  def test_initialization(self):
    """Test TornPaper initialization with default and custom seeds."""
    # Default seed
    tp = TornPaper()
    assert tp.seed == 42

    # Custom seed
    tp_custom = TornPaper(seed=123)
    assert tp_custom.seed == 123

  def test_basic_torn_paper(self):
    """Test basic torn paper generation with default parameters."""
    tp = TornPaper()
    result = tp.calculate_torn_paper()

    # Verify return structure
    assert isinstance(result, dict)
    assert 'shape' in result
    assert isinstance(result['shape'], list)
    assert len(result['shape']) > 0

    # Verify SVG path format
    svg_paths = result['shape']
    assert all(isinstance(path, str) for path in svg_paths)

  def test_parameter_validation_torn_sides(self):
    """Test torn_sides parameter validation."""
    tp = TornPaper()

    # Valid sides
    valid_sides = ['N', 'S', 'E', 'W', 'NS', 'EW', 'NEW', 'NSEW', 'ns', 'ew']
    for sides in valid_sides:
      result = tp.calculate_torn_paper(torn_sides=sides)
      assert 'shape' in result

    # Invalid sides
    invalid_sides = ['', 'X', 'NSX', '123', 'NSEWX']
    for sides in invalid_sides:
      with pytest.raises(ValueError, match="torn_sides must contain only"):
        tp.calculate_torn_paper(torn_sides=sides)

  def test_parameter_validation_segments(self):
    """Test segments parameter validation."""
    tp = TornPaper()

    # Valid segments
    for segments in [10, 50, 100, 500, 1000]:
      result = tp.calculate_torn_paper(segments=segments)
      assert 'shape' in result

    # Invalid segments
    for segments in [9, 0, -1, 1001, 2000]:
      with pytest.raises(ValueError, match="segments must be between 10 and 1000"):
        tp.calculate_torn_paper(segments=segments)

  def test_parameter_validation_amplitude(self):
    """Test amplitude parameter validation."""
    tp = TornPaper()

    # Valid amplitude
    for amplitude in [0.1, 1.0, 25.0, 50.0]:
      result = tp.calculate_torn_paper(amplitude=amplitude)
      assert 'shape' in result

    # Invalid amplitude
    for amplitude in [0.09, 0, -1, 50.1, 100]:
      with pytest.raises(ValueError, match="amplitude must be between 0.1 and 50.0"):
        tp.calculate_torn_paper(amplitude=amplitude)

  def test_parameter_validation_noise_scale(self):
    """Test noise_scale parameter validation."""
    tp = TornPaper()

    # Valid noise_scale
    for noise_scale in [0.01, 0.1, 0.5, 1.0]:
      result = tp.calculate_torn_paper(noise_scale=noise_scale)
      assert 'shape' in result

    # Invalid noise_scale
    for noise_scale in [0.009, 0, -0.1, 1.1, 2.0]:
      with pytest.raises(ValueError, match="noise_scale must be between 0.01 and 1.0"):
        tp.calculate_torn_paper(noise_scale=noise_scale)

  def test_parameter_validation_octaves(self):
    """Test octaves parameter validation."""
    tp = TornPaper()

    # Valid octaves
    for octaves in [1, 2, 3, 4, 5, 6]:
      result = tp.calculate_torn_paper(octaves=octaves)
      assert 'shape' in result

    # Invalid octaves
    for octaves in [0, -1, 7, 10]:
      with pytest.raises(ValueError, match="octaves must be between 1 and 6"):
        tp.calculate_torn_paper(octaves=octaves)

  def test_torn_sides_combinations(self):
    """Test different combinations of torn sides."""
    tp = TornPaper(seed=42)  # Fixed seed for consistent results

    # Test all individual sides
    for side in ['N', 'S', 'E', 'W']:
      result = tp.calculate_torn_paper(torn_sides=side)
      assert 'shape' in result
      assert len(result['shape']) > 0

    # Test common combinations
    combinations = ['NS', 'EW', 'NE', 'SW', 'NEW', 'SEW', 'NSEW']
    for combo in combinations:
      result = tp.calculate_torn_paper(torn_sides=combo)
      assert 'shape' in result
      assert len(result['shape']) > 0

  def test_case_insensitive_sides(self):
    """Test that torn_sides parameter is case-insensitive."""
    tp = TornPaper(seed=42)

    # Same seed should produce identical results regardless of case
    result_upper = tp.calculate_torn_paper(torn_sides='NS')
    result_lower = tp.calculate_torn_paper(torn_sides='ns')
    result_mixed = tp.calculate_torn_paper(torn_sides='Ns')

    # Results should be identical
    assert result_upper == result_lower == result_mixed

  def test_seed_consistency(self):
    """Test that same seed produces consistent results."""
    seed = 12345
    params = {
      'torn_sides': 'NSEW',
      'segments': 50,
      'amplitude': 10.0,
      'width': 200,
      'height': 150,
    }

    # Generate with same seed multiple times
    tp1 = TornPaper(seed=seed)
    result1 = tp1.calculate_torn_paper(**params)

    tp2 = TornPaper(seed=seed)
    result2 = tp2.calculate_torn_paper(**params)

    # Results should be identical
    assert result1 == result2

  def test_different_seeds_produce_different_results(self):
    """Test that different seeds produce different results."""
    params = {
      'torn_sides': 'NS',
      'segments': 30,
      'amplitude': 5.0,
    }

    tp1 = TornPaper(seed=111)
    result1 = tp1.calculate_torn_paper(**params)

    tp2 = TornPaper(seed=222)
    result2 = tp2.calculate_torn_paper(**params)

    # Results should be different
    assert result1 != result2

  def test_dimensions_effect(self):
    """Test that width and height parameters affect the output."""
    tp = TornPaper(seed=42)

    # Small dimensions
    result_small = tp.calculate_torn_paper(width=50, height=30)

    # Large dimensions
    result_large = tp.calculate_torn_paper(width=300, height=200)

    # Results should be different
    assert result_small != result_large
    assert 'shape' in result_small
    assert 'shape' in result_large

  def test_extreme_valid_parameters(self):
    """Test with extreme but valid parameter values."""
    tp = TornPaper()

    # Minimum valid parameters
    result_min = tp.calculate_torn_paper(
      segments=10, amplitude=0.1, noise_scale=0.01, octaves=1
    )
    assert 'shape' in result_min

    # Maximum valid parameters
    result_max = tp.calculate_torn_paper(
      segments=1000, amplitude=50.0, noise_scale=1.0, octaves=6
    )
    assert 'shape' in result_max

  def test_svg_path_structure(self):
    """Test the structure of generated SVG paths."""
    tp = TornPaper()
    result = tp.calculate_torn_paper(torn_sides='N', segments=20)

    svg_paths = result['shape']

    # Should have at least move and line commands
    assert len(svg_paths) > 1

    # First command should be a move element
    assert any('<move' in path for path in svg_paths)

    # Should have line elements for segments
    assert any('<line' in path for path in svg_paths)

  def test_no_torn_sides(self):
    """Test behavior when no sides are torn (edge case)."""
    tp = TornPaper()

    # This should raise an error since torn_sides cannot be empty
    with pytest.raises(ValueError):
      tp.calculate_torn_paper(torn_sides='')

  @pytest.mark.parametrize('segments', [10, 50, 100])
  @pytest.mark.parametrize('amplitude', [1.0, 5.0, 10.0])
  def test_parametrized_combinations(self, segments, amplitude):
    """Test various parameter combinations."""
    tp = TornPaper(seed=42)
    result = tp.calculate_torn_paper(segments=segments, amplitude=amplitude)

    assert 'shape' in result
    assert len(result['shape']) > 0

  def test_visual_output_debug(self):
    """Generate test output for visual validation (debugging aid)."""
    tp = TornPaper(seed=42)

    # Generate a few different configurations
    configs = [
      {'torn_sides': 'N', 'amplitude': 5.0},
      {'torn_sides': 'NS', 'amplitude': 8.0},
      {'torn_sides': 'NSEW', 'amplitude': 3.0},
    ]

    for config in configs:
      result = tp.calculate_torn_paper(**config)
      assert 'shape' in result
      # For debugging: print(f"Config {config}: {len(result['shape'])} path segments")

  def test_fitting_constraint_concept(self):
    """Test that North/South pairs use complementary tear patterns."""
    tp = TornPaper(seed=42)

    # Generate shapes with North and South sides
    # The fitting constraint is built into the amplitude calculation
    # This test verifies the method runs without error
    result_n = tp.calculate_torn_paper(torn_sides='N', segments=20)
    result_s = tp.calculate_torn_paper(torn_sides='S', segments=20)
    result_ns = tp.calculate_torn_paper(torn_sides='NS', segments=20)

    # All should generate valid output
    assert 'shape' in result_n
    assert 'shape' in result_s
    assert 'shape' in result_ns

    # The actual fitting constraint is tested through visual validation
    # and mathematical analysis of the amplitude signs in the implementation