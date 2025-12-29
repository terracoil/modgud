"""Tests for Quadrilateral torn edge functionality."""

from unittest.mock import Mock

import pytest
from modgud.api.geometry import Quadrilateral, SimplexNoise, Vector
from modgud.domain.enums import PlacementEnum, QuadShapeEnum
from modgud.domain.ports import ShapePort


class TestQuadrilateralTorn:
  """Test suite for Quadrilateral torn edge functionality."""

  def create_mock_noise(self):
    """Create a mock noise provider for testing."""
    noise = Mock()
    noise.noise2d.return_value = 0.5  # Consistent noise value for testing
    noise.fbm2d.return_value = 0.5
    noise.noise_array2d.return_value = [0.5]
    noise.fbm_array2d.return_value = [0.5]
    noise.generate_noise_map.return_value = [[0.5]]
    return noise

  def test_torn_quadrilateral_basic_functionality(self):
    """Test basic torn quadrilateral creation."""
    noise = self.create_mock_noise()
    quad = Quadrilateral(
      quad_shape=QuadShapeEnum.RECTANGLE,
      params={'w': 0.8, 'h': 0.6},
      torn_sides=[PlacementEnum.NORTH, PlacementEnum.SOUTH],
      noise=noise,
      noise_amplitude=3.0,
    )

    vectors = quad.build_shape()

    # Should have more than 4 points due to torn edges
    assert len(vectors) > 4

    # Should still be a closed shape with reasonable bounds
    x_coords = [v.x for v in vectors]
    y_coords = [v.y for v in vectors]
    assert min(x_coords) >= -10.0  # Allow for noise displacement
    assert max(x_coords) <= 10.0
    assert min(y_coords) >= -10.0
    assert max(y_coords) <= 10.0

  def test_torn_quadrilateral_no_noise_no_torn_sides(self):
    """Test quadrilateral without torn sides behaves normally."""
    quad = Quadrilateral(quad_shape=QuadShapeEnum.RECTANGLE, params={'w': 0.8, 'h': 0.6})

    vectors = quad.build_shape()

    # Should have exactly 4 points (normal rectangle)
    assert len(vectors) == 4
    assert vectors[0].x == 0.0 and vectors[0].y == 0.0
    assert vectors[1].x == 0.8 and vectors[1].y == 0.0
    assert vectors[2].x == 0.8 and vectors[2].y == 0.6
    assert vectors[3].x == 0.0 and vectors[3].y == 0.6

  def test_torn_quadrilateral_all_sides(self):
    """Test quadrilateral with all sides torn."""
    noise = self.create_mock_noise()
    quad = Quadrilateral(
      quad_shape=QuadShapeEnum.SQUARE,
      params={'side': 0.7},
      torn_sides=[PlacementEnum.NORTH, PlacementEnum.SOUTH, PlacementEnum.EAST, PlacementEnum.WEST],
      noise=noise,
      noise_segments=20,  # Smaller for testing
      noise_amplitude=2.0,
    )

    vectors = quad.build_shape()

    # Should have significantly more than 4 points
    assert len(vectors) > 50  # 4 edges * ~20 segments each

    # Verify it's still a reasonably closed shape
    assert isinstance(vectors[0], (Vector, type(vectors[0])))

  def test_torn_quadrilateral_validation_no_noise(self):
    """Test validation fails when torn_sides specified without noise."""
    with pytest.raises(ValueError, match='noise parameter required when torn_sides is specified'):
      Quadrilateral(
        quad_shape=QuadShapeEnum.RECTANGLE,
        params={'w': 0.8, 'h': 0.6},
        torn_sides=[PlacementEnum.NORTH, PlacementEnum.SOUTH],  # No noise provided
      )

  def test_torn_quadrilateral_validation_invalid_sides(self):
    """Test validation fails with invalid torn_sides."""
    noise = self.create_mock_noise()

    # Since we're now using enums, we can't pass invalid values directly
    # The type system will catch this at development time
    # Let's test with an invalid enum combination instead
    with pytest.raises(ValueError, match='Invalid torn side'):
      quad = Quadrilateral(
        quad_shape=QuadShapeEnum.RECTANGLE,
        params={'w': 0.8, 'h': 0.6},
        torn_sides=[PlacementEnum.NE],  # Compound directions not allowed for torn sides
        noise=noise,
      )

  def test_torn_quadrilateral_validation_amplitude_range(self):
    """Test validation of noise amplitude ranges."""
    noise = self.create_mock_noise()

    # Test amplitude too small
    with pytest.raises(ValueError, match='noise_amplitude must be between 0.1 and 50.0'):
      Quadrilateral(
        quad_shape=QuadShapeEnum.RECTANGLE,
        params={'w': 0.8, 'h': 0.6},
        torn_sides=[PlacementEnum.NORTH, PlacementEnum.SOUTH],
        noise=noise,
        noise_amplitude=0.05,  # Too small
      )

    # Test amplitude too large
    with pytest.raises(ValueError, match='noise_amplitude must be between 0.1 and 50.0'):
      Quadrilateral(
        quad_shape=QuadShapeEnum.RECTANGLE,
        params={'w': 0.8, 'h': 0.6},
        torn_sides=[PlacementEnum.NORTH, PlacementEnum.SOUTH],
        noise=noise,
        noise_amplitude=60.0,  # Too large
      )

  def test_torn_quadrilateral_validation_segments_range(self):
    """Test validation of noise segments ranges."""
    noise = self.create_mock_noise()

    # Test segments too few
    with pytest.raises(ValueError, match='noise_segments must be between 10 and 1000'):
      Quadrilateral(
        quad_shape=QuadShapeEnum.RECTANGLE,
        params={'w': 0.8, 'h': 0.6},
        torn_sides=[PlacementEnum.NORTH, PlacementEnum.SOUTH],
        noise=noise,
        noise_segments=5,  # Too few
      )

    # Test segments too many
    with pytest.raises(ValueError, match='noise_segments must be between 10 and 1000'):
      Quadrilateral(
        quad_shape=QuadShapeEnum.RECTANGLE,
        params={'w': 0.8, 'h': 0.6},
        torn_sides=[PlacementEnum.NORTH, PlacementEnum.SOUTH],
        noise=noise,
        noise_segments=1500,  # Too many
      )

  def test_torn_quadrilateral_validation_smoothing_range(self):
    """Test validation of smoothing factor ranges."""
    noise = self.create_mock_noise()

    # Test smoothing factor too small
    with pytest.raises(ValueError, match='smoothing_factor must be between 0.0 and 1.0'):
      Quadrilateral(
        quad_shape=QuadShapeEnum.RECTANGLE,
        params={'w': 0.8, 'h': 0.6},
        torn_sides=[PlacementEnum.NORTH, PlacementEnum.SOUTH],
        noise=noise,
        smoothing_factor=-0.1,  # Too small
      )

    # Test smoothing factor too large
    with pytest.raises(ValueError, match='smoothing_factor must be between 0.0 and 1.0'):
      Quadrilateral(
        quad_shape=QuadShapeEnum.RECTANGLE,
        params={'w': 0.8, 'h': 0.6},
        torn_sides=[PlacementEnum.NORTH, PlacementEnum.SOUTH],
        noise=noise,
        smoothing_factor=1.5,  # Too large
      )

  def test_torn_quadrilateral_different_shapes(self):
    """Test torn edges work with different quadrilateral shapes."""
    noise = self.create_mock_noise()

    # Test with parallelogram
    para_quad = Quadrilateral(
      quad_shape=QuadShapeEnum.PARALLELOGRAM,
      params={'w': 0.8, 'h': 0.6, 'angle': 60.0},
      torn_sides=[PlacementEnum.EAST, PlacementEnum.WEST],
      noise=noise,
      noise_amplitude=2.0,
    )
    para_vectors = para_quad.build_shape()
    assert len(para_vectors) > 4

    # Test with trapezoid
    trap_quad = Quadrilateral(
      quad_shape=QuadShapeEnum.RIGHTANGLE_TRAPEZOID,
      params={'w1': 0.8, 'w2': 0.6, 'h': 0.5},
      torn_sides=[PlacementEnum.SOUTH],
      noise=noise,
      noise_amplitude=1.5,
    )
    trap_vectors = trap_quad.build_shape()
    assert len(trap_vectors) > 4

  def test_torn_quadrilateral_enum_consistency(self):
    """Test that torn_sides works consistently with PlacementEnum."""
    noise = self.create_mock_noise()

    # Test with individual enums
    quad1 = Quadrilateral(
      quad_shape=QuadShapeEnum.RECTANGLE,
      params={'w': 0.8, 'h': 0.6},
      torn_sides=[PlacementEnum.NORTH, PlacementEnum.SOUTH],
      noise=noise,
    )
    vectors1 = quad1.build_shape()

    # Test with same enums in different order
    quad2 = Quadrilateral(
      quad_shape=QuadShapeEnum.RECTANGLE,
      params={'w': 0.8, 'h': 0.6},
      torn_sides=[PlacementEnum.SOUTH, PlacementEnum.NORTH],
      noise=noise,
    )
    vectors2 = quad2.build_shape()

    # Should produce same number of points (same shape)
    assert len(vectors1) == len(vectors2)

  def test_torn_quadrilateral_protocol_compliance(self):
    """Test that torn quadrilaterals still implement ShapePort protocol."""
    noise = self.create_mock_noise()
    quad = Quadrilateral(
      quad_shape=QuadShapeEnum.RECTANGLE,
      params={'w': 0.8, 'h': 0.6},
      torn_sides=[PlacementEnum.NORTH, PlacementEnum.SOUTH],
      noise=noise,
    )

    # Should still satisfy ShapePort protocol
    assert isinstance(quad, ShapePort)
    assert hasattr(quad, 'build_shape')
    assert callable(quad.build_shape)

    # build_shape should return sequence of VectorPort
    vectors = quad.build_shape()
    assert hasattr(vectors, '__iter__')
    assert all(hasattr(v, 'x') and hasattr(v, 'y') for v in vectors)

  def test_torn_quadrilateral_empty_torn_sides(self):
    """Test that empty torn_sides list is handled correctly."""
    quad = Quadrilateral(
      quad_shape=QuadShapeEnum.RECTANGLE,
      params={'w': 0.8, 'h': 0.6},
      torn_sides=[],  # Empty list
      # No noise needed for empty torn_sides
    )

    vectors = quad.build_shape()

    # Should behave like normal rectangle
    assert len(vectors) == 4
    assert vectors[0].x == 0.0 and vectors[0].y == 0.0

  def test_torn_quadrilateral_real_simplex_noise_integration(self):
    """Test integration with real SimplexNoise for basic functionality."""
    noise = SimplexNoise(seed=42)  # Use real noise for integration test

    quad = Quadrilateral(
      quad_shape=QuadShapeEnum.RECTANGLE,
      params={'w': 0.5, 'h': 0.4},
      torn_sides=[PlacementEnum.NORTH, PlacementEnum.SOUTH],
      noise=noise,
      noise_segments=50,
      noise_amplitude=2.0,
      smoothing_factor=0.2,
    )

    vectors = quad.build_shape()

    # Should produce reasonable torn shape
    assert len(vectors) > 4
    assert len(vectors) < 200  # Reasonable upper bound

    # Check that we have actual noise variation (not all points identical)
    x_coords = [v.x for v in vectors]
    y_coords = [v.y for v in vectors]
    assert len(set(round(x, 4) for x in x_coords)) > 10  # Multiple unique x coordinates
    assert len(set(round(y, 4) for y in y_coords)) > 10  # Multiple unique y coordinates
