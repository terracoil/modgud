"""Tests for Quadrilateral torn notch functionality."""

import pytest
from modgud.domain.enums import OrdinalEnum, QuadShapeEnum
from modgud.util.geo import Quadrilateral, SimplexNoise


class TestQuadrilateralTornNotch:
  """Test suite for Quadrilateral torn notch functionality."""

  @pytest.fixture
  def noise(self):
    """Create a noise provider for testing."""
    return SimplexNoise(42)  # Fixed seed for reproducible tests

  def test_torn_notch_single_side(self, noise):
    """Test a single side with both torn edge and notch."""
    quad = Quadrilateral(
      quad_shape=QuadShapeEnum.RECTANGLE,
      params={'w': 1.0, 'h': 1.0},
      torn_sides=[OrdinalEnum.NORTH],
      notch_sides=[OrdinalEnum.NORTH],
      notch_size=0.3,
      notch_depth=0.2,
      noise=noise,
      noise_amplitude=5.0,
      noise_segments=50,
    )

    vertices = quad.build_shape()

    # Should have many more points than a basic rectangle due to torn notch
    assert len(vertices) > 20  # Torn notch creates many points

    # The shape should still be closed (forms a valid polygon)
    # Check that we have reasonable bounds
    xs = [v.x for v in vertices]
    ys = [v.y for v in vertices]

    # Should extend beyond original bounds due to notch
    assert max(ys) > 1.0  # North notch extends upward
    # Noise can create significant variations
    assert min(xs) >= -1.0  # Reasonable bounds with noise
    assert max(xs) <= 2.0  # Reasonable bounds with noise

  def test_torn_notch_mixed_configuration(self, noise):
    """Test mixed configuration with torn edges, clean notches, and torn notches."""
    quad = Quadrilateral(
      quad_shape=QuadShapeEnum.RECTANGLE,
      params={'w': 1.0, 'h': 1.0},
      torn_sides=[OrdinalEnum.NORTH, OrdinalEnum.SOUTH],  # North and South torn
      notch_sides=[OrdinalEnum.NORTH, OrdinalEnum.EAST],  # North and East notched
      notch_size=0.25,
      notch_depth=0.15,
      noise=noise,
      noise_amplitude=3.0,
      noise_segments=40,
    )

    vertices = quad.build_shape()

    # Should have many points due to torn edges and notches
    assert len(vertices) > 30

    # Check bounds
    xs = [v.x for v in vertices]
    ys = [v.y for v in vertices]

    # North: torn notch (extends up with noise)
    assert max(ys) > 1.0

    # South: torn edge only (extends down with noise)
    assert min(ys) < 0.0

    # East: clean notch (extends right cleanly)
    assert max(xs) > 1.0

  def test_torn_notch_no_noise_provider(self):
    """Test that torn notches require a noise provider."""
    # Without noise, can only have clean notches, not torn sides
    quad = Quadrilateral(
      quad_shape=QuadShapeEnum.RECTANGLE,
      params={'w': 1.0, 'h': 1.0},
      notch_sides=[OrdinalEnum.NORTH],  # Only notch, no torn sides
      notch_size=0.3,
      notch_depth=0.2,
      # No noise provider
    )

    # Should apply clean notch
    vertices = quad.build_shape()

    # Should have exactly 8 vertices (rectangle with one notch)
    assert len(vertices) == 8

  def test_torn_notch_multiple_sides(self, noise):
    """Test torn notches on multiple sides."""
    quad = Quadrilateral(
      quad_shape=QuadShapeEnum.RECTANGLE,
      params={'w': 1.0, 'h': 1.0},
      torn_sides=[OrdinalEnum.NORTH, OrdinalEnum.SOUTH, OrdinalEnum.EAST, OrdinalEnum.WEST],
      notch_sides=[OrdinalEnum.NORTH, OrdinalEnum.SOUTH],
      notch_size=0.2,
      notch_depth=0.1,
      noise=noise,
      noise_amplitude=2.0,
      noise_segments=30,
    )

    vertices = quad.build_shape()

    # Should have many points from torn edges and torn notches
    assert len(vertices) > 50

    # All sides should have some variation from noise
    xs = [v.x for v in vertices]
    ys = [v.y for v in vertices]

    # Check that bounds are extended in all directions
    assert min(xs) < 0.0  # West side extends left
    assert max(xs) > 1.0  # East side extends right
    assert min(ys) < 0.0  # South notch extends down
    assert max(ys) > 1.0  # North notch extends up

  def test_torn_notch_with_offset(self, noise):
    """Test torn notch with offset."""
    quad = Quadrilateral(
      quad_shape=QuadShapeEnum.RECTANGLE,
      params={'w': 1.0, 'h': 1.0},
      torn_sides=[OrdinalEnum.NORTH],
      notch_sides=[OrdinalEnum.NORTH],
      notch_size=0.3,
      notch_depth=0.2,
      notch_offset=0.25,  # Offset to the right
      noise=noise,
      noise_amplitude=3.0,
      noise_segments=40,
    )

    vertices = quad.build_shape()

    # Should have many points from torn notch
    assert len(vertices) > 20

    # The notch should still be offset even with torn edges
    # Find points that are part of the notch (y > 1.0)
    notch_points = [v for v in vertices if v.y > 1.05]
    if notch_points:
      avg_x = sum(p.x for p in notch_points) / len(notch_points)
      # Should be offset to the right of center
      assert avg_x > 0.6  # Approximate due to noise

  def test_torn_notch_zero_parameters(self, noise):
    """Test torn notch with zero size or depth."""
    # Zero size
    quad_zero_size = Quadrilateral(
      quad_shape=QuadShapeEnum.RECTANGLE,
      params={'w': 1.0, 'h': 1.0},
      torn_sides=[OrdinalEnum.NORTH],
      notch_sides=[OrdinalEnum.NORTH],
      notch_size=0.0,  # Zero size
      notch_depth=0.2,
      noise=noise,
    )

    vertices_zero_size = quad_zero_size.build_shape()
    # Should just have torn edge, no notch
    assert len(vertices_zero_size) > 4  # More than rectangle due to torn edge

    # Zero depth
    quad_zero_depth = Quadrilateral(
      quad_shape=QuadShapeEnum.RECTANGLE,
      params={'w': 1.0, 'h': 1.0},
      torn_sides=[OrdinalEnum.NORTH],
      notch_sides=[OrdinalEnum.NORTH],
      notch_size=0.2,
      notch_depth=0.0,  # Zero depth
      noise=noise,
    )

    vertices_zero_depth = quad_zero_depth.build_shape()
    # Should just have torn edge, no notch
    assert len(vertices_zero_depth) > 4  # More than rectangle due to torn edge

  def test_torn_notch_different_shapes(self, noise):
    """Test torn notches work with different quadrilateral shapes."""
    # Test with square
    quad_square = Quadrilateral(
      quad_shape=QuadShapeEnum.SQUARE,
      params={'side': 0.8},
      torn_sides=[OrdinalEnum.EAST],
      notch_sides=[OrdinalEnum.EAST],
      notch_size=0.2,
      notch_depth=0.1,
      noise=noise,
      noise_amplitude=2.0,
    )
    vertices_square = quad_square.build_shape()
    assert len(vertices_square) > 10  # Has torn notch

    # Test with parallelogram
    quad_para = Quadrilateral(
      quad_shape=QuadShapeEnum.PARALLELOGRAM,
      params={'w': 0.8, 'h': 0.6, 'angle': 60.0},
      torn_sides=[OrdinalEnum.SOUTH],
      notch_sides=[OrdinalEnum.SOUTH],
      notch_size=0.15,
      notch_depth=0.1,
      noise=noise,
      noise_amplitude=2.0,
    )
    vertices_para = quad_para.build_shape()
    assert len(vertices_para) > 10  # Has torn notch

  def test_torn_notch_amplitude_scaling(self, noise):
    """Test that torn notch edges have appropriate amplitude scaling."""
    # Create two quads - one with torn edge, one with torn notch
    quad_torn_edge = Quadrilateral(
      quad_shape=QuadShapeEnum.RECTANGLE,
      params={'w': 1.0, 'h': 1.0},
      torn_sides=[OrdinalEnum.NORTH],
      noise=noise,
      noise_amplitude=10.0,  # High amplitude
    )

    quad_torn_notch = Quadrilateral(
      quad_shape=QuadShapeEnum.RECTANGLE,
      params={'w': 1.0, 'h': 1.0},
      torn_sides=[OrdinalEnum.NORTH],
      notch_sides=[OrdinalEnum.NORTH],
      notch_size=0.3,
      notch_depth=0.2,
      noise=noise,
      noise_amplitude=10.0,  # Same high amplitude
    )

    vertices_edge = quad_torn_edge.build_shape()
    vertices_notch = quad_torn_notch.build_shape()

    # Both should have noise applied
    assert len(vertices_edge) > 4
    assert len(vertices_notch) > 4  # Has torn notch

    # The key difference is that torn notch creates an indentation
    # Check that the notch shape extends beyond the original bounds
    ys_notch = [v.y for v in vertices_notch]
    assert max(ys_notch) > 1.0  # Notch extends upward

    # Both shapes should have noise-induced variation on the NORTH edge
    # Check variation in y-coordinates for points on the north edge
    # For torn edge, the north edge should have variation
    north_edge_ys = [v.y for v in vertices_edge if v.x >= 0 and v.x <= 1.0]
    assert max(north_edge_ys) - min(north_edge_ys) > 0.1  # Noise creates variation

    # Torn notch shape has the notch feature
    # Both shapes have complexity from noise
    assert len(vertices_edge) > 10  # Torn edge creates many points
    assert len(vertices_notch) > 10  # Torn notch also creates many points
