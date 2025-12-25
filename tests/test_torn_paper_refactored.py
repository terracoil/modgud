"""Tests for refactored TornPaper dataclass implementation."""

import pytest
from modgud.api.geometry import SimplexNoise, TornPaper

from tests.test_shape_utils import ShapeTestUtils


class TestTornPaperRefactored:
  """Test the refactored TornPaper dataclass implementation."""

  def test_dataclass_immutability(self):
    """Test that TornPaper is immutable (frozen=True)."""
    noise = SimplexNoise(seed=42)
    tp = TornPaper(noise=noise, torn_sides='NS', segments=50)

    # Test that we can't modify attributes
    ShapeTestUtils.assert_dataclass_immutability(tp, 'torn_sides', 'EW')
    ShapeTestUtils.assert_dataclass_immutability(tp, 'segments', 100)
    ShapeTestUtils.assert_dataclass_immutability(tp, 'amplitude', 10.0)

  def test_constructor_parameters(self):
    """Test that all parameters work in constructor."""
    noise = SimplexNoise(seed=42)
    tp = TornPaper(
      noise=noise,
      torn_sides='NSEW',
      segments=200,
      amplitude=15.0,
      width=200,
      height=150,
      smoothing_factor=0.3,
    )

    # Verify parameters are set correctly
    assert tp.noise == noise
    assert tp.torn_sides == 'NSEW'
    assert tp.segments == 200
    assert tp.amplitude == 15.0
    assert tp.width == 200
    assert tp.height == 150
    assert tp.smoothing_factor == 0.3

    # Verify build_shape works
    result = tp.build_shape()
    ShapeTestUtils.assert_valid_vector_sequence(result)

  def test_validation_in_constructor(self):
    """Test that validation happens in constructor (__post_init__)."""
    noise = SimplexNoise(seed=42)

    # Invalid torn_sides should fail at construction
    with pytest.raises(ValueError, match='torn_sides must contain only'):
      TornPaper(noise=noise, torn_sides='X')

    # Invalid segments should fail at construction
    with pytest.raises(ValueError, match='segments must be between 10 and 1000'):
      TornPaper(noise=noise, segments=5)

    # Invalid amplitude should fail at construction
    with pytest.raises(ValueError, match='amplitude must be between 0.1 and 50.0'):
      TornPaper(noise=noise, amplitude=0.05)

    # Invalid smoothing_factor should fail at construction
    with pytest.raises(ValueError, match='smoothing_factor must be between 0.0 and 1.0'):
      TornPaper(noise=noise, smoothing_factor=1.5)

  def test_return_type_is_vector_sequence(self):
    """Test that build_shape returns Sequence[VectorPort], not SVG dict."""
    noise = SimplexNoise(seed=42)
    tp = TornPaper(noise=noise, torn_sides='NS')

    result = tp.build_shape()

    # Should be a sequence of vectors
    ShapeTestUtils.assert_valid_vector_sequence(result)

    # Should NOT be the old dictionary format
    assert not isinstance(result, dict)
    assert not hasattr(result, 'keys')

  def test_backward_compatibility_conversion(self):
    """Test that results can be converted to legacy format."""
    noise = SimplexNoise(seed=42)
    tp = TornPaper(noise=noise, torn_sides='NS', segments=20)

    vectors = tp.build_shape()
    legacy_dict = ShapeTestUtils.assert_backward_compatibility(vectors)

    # Verify structure matches old format
    assert 'shape' in legacy_dict
    assert isinstance(legacy_dict['shape'], list)
    assert len(legacy_dict['shape']) > 0

    # Verify SVG commands
    svg_commands = legacy_dict['shape']
    assert any('<path' in cmd for cmd in svg_commands)
    assert any('<move' in cmd for cmd in svg_commands)

  def test_same_seed_reproducibility(self):
    """Test that same noise seed produces reproducible results."""
    # Create two instances with same noise
    noise1 = SimplexNoise(seed=123, scale=0.1, amplitude=2.0)
    noise2 = SimplexNoise(seed=123, scale=0.1, amplitude=2.0)

    tp1 = TornPaper(noise=noise1, torn_sides='NS', segments=30, amplitude=5.0)
    tp2 = TornPaper(noise=noise2, torn_sides='NS', segments=30, amplitude=5.0)

    result1 = tp1.build_shape()
    result2 = tp2.build_shape()

    # Should produce identical results
    assert result1 == result2

  def test_different_parameters_produce_different_results(self):
    """Test that different parameters produce different shapes."""
    noise = SimplexNoise(seed=42)

    tp1 = TornPaper(noise=noise, torn_sides='N', segments=20)
    tp2 = TornPaper(noise=noise, torn_sides='S', segments=20)
    tp3 = TornPaper(noise=noise, torn_sides='N', segments=50)

    result1 = tp1.build_shape()
    result2 = tp2.build_shape()
    result3 = tp3.build_shape()

    # Different torn_sides should produce different results
    assert result1 != result2

    # Different segments should produce different results
    assert result1 != result3
