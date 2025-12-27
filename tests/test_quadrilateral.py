"""Tests for Quadrilateral shape generator class."""

import pytest
from modgud.api.geometry import Quadrilateral, Vector
from modgud.domain.ports import ShapePort


class TestQuadrilateral:
  """Test suite for Quadrilateral shape generator."""

  def test_quadrilateral_implements_shape_port(self):
    """Test that Quadrilateral implements ShapePort protocol."""
    quad = Quadrilateral(shape_type='rectangle', params={'w': 2.0, 'h': 3.0})

    # Test structural protocol compliance
    assert hasattr(quad, 'build_shape')
    assert callable(quad.build_shape)
    assert isinstance(quad, ShapePort)

  def test_quadrilateral_default_construction(self):
    """Test default Quadrilateral construction."""
    quad = Quadrilateral()

    assert quad.shape_type == 'rectangle'
    assert quad.params == {}

  def test_quadrilateral_build_shape_rectangle(self):
    """Test building a rectangle shape."""
    quad = Quadrilateral(shape_type='rect', params={'w': 0.8, 'h': 0.6})
    vectors = quad.build_shape()

    assert len(vectors) == 4
    # Check basic rectangle properties
    assert vectors[0].x == 0.0 and vectors[0].y == 0.0  # bottom-left
    assert vectors[1].x == 0.8 and vectors[1].y == 0.0  # bottom-right
    assert vectors[2].x == 0.8 and vectors[2].y == 0.6  # top-right
    assert vectors[3].x == 0.0 and vectors[3].y == 0.6  # top-left

  def test_quadrilateral_build_shape_square(self):
    """Test building a square shape."""
    quad = Quadrilateral(shape_type='square', params={'side': 0.7})
    vectors = quad.build_shape()

    assert len(vectors) == 4
    # Check basic square properties
    assert vectors[0].x == 0.0 and vectors[0].y == 0.0  # bottom-left
    assert vectors[1].x == 0.7 and vectors[1].y == 0.0  # bottom-right
    assert vectors[2].x == 0.7 and vectors[2].y == 0.7  # top-right
    assert vectors[3].x == 0.0 and vectors[3].y == 0.7  # top-left

  def test_quadrilateral_build_shape_parallelogram(self):
    """Test building a parallelogram shape."""
    quad = Quadrilateral(shape_type='parallelogram', params={'w': 0.8, 'h': 0.6, 'angle': 60.0})
    vectors = quad.build_shape()

    assert len(vectors) == 4
    # Parallelogram should have parallel opposite sides
    # Bottom side vector
    bottom_vec = Vector(vectors[1].x - vectors[0].x, vectors[1].y - vectors[0].y)
    # Top side vector
    top_vec = Vector(vectors[2].x - vectors[3].x, vectors[2].y - vectors[3].y)

    # Bottom and top vectors should be parallel (same direction)
    assert abs(bottom_vec.x - top_vec.x) < 1e-6
    assert abs(bottom_vec.y - top_vec.y) < 1e-6

  def test_quadrilateral_invalid_shape_type(self):
    """Test error handling for unknown shape type."""
    quad = Quadrilateral(shape_type='hexagon', params={'side': 0.5})

    with pytest.raises(ValueError, match='Unknown shape type: hexagon'):
      quad.build_shape()

  def test_quadrilateral_parameter_validation_positive(self):
    """Test parameter validation requires positive values."""
    with pytest.raises(ValueError, match='Parameter side must be positive'):
      Quadrilateral(shape_type='square', params={'side': -1.0})

  def test_quadrilateral_parameter_validation_zero(self):
    """Test parameter validation rejects zero values."""
    with pytest.raises(ValueError, match='Parameter w must be positive'):
      Quadrilateral(shape_type='rect', params={'w': 0.0, 'h': 0.5})

  def test_quadrilateral_immutability(self):
    """Test that Quadrilateral instances are immutable (frozen dataclass)."""
    quad = Quadrilateral(shape_type='square', params={'side': 0.5})

    # Should not be able to modify shape_type via normal assignment
    with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
      quad.shape_type = 'rectangle'

    # Test frozen behavior - try to modify an attribute that should be frozen
    # Note: The actual frozen behavior varies by Python implementation
    # Let's verify that the dataclass is indeed frozen by checking the class attributes
    import dataclasses

    assert dataclasses.is_dataclass(quad)

    # Verify that attempting direct modification fails
    try:
      quad.shape_type = 'rectangle'
      # If we get here, the assignment succeeded, which it shouldn't for frozen dataclass
      assert False, 'Expected assignment to fail on frozen dataclass'
    except (dataclasses.FrozenInstanceError, AttributeError):
      # This is expected - frozen dataclass should prevent assignment
      pass

  def test_quadrilateral_factory_methods_available(self):
    """Test that all expected shape factory methods are available."""
    quad = Quadrilateral()

    # Check that factory methods exist
    expected_methods = [
      'square',
      'rect',
      'parallelogram',
      'rhombus',
      'rightangle_trapezoid',
      'general_trapezoid',
      'isosceles_trapezoid',
      'kite',
    ]

    for method_name in expected_methods:
      assert hasattr(quad, method_name)
      assert callable(getattr(quad, method_name))

  def test_quadrilateral_dry_principle_square_uses_rectangle(self):
    """Test DRY principle: square should be rectangle with equal sides."""
    # Create square and rectangle with same dimensions
    square_quad = Quadrilateral(shape_type='square', params={'side': 0.6})
    rect_quad = Quadrilateral(shape_type='rect', params={'w': 0.6, 'h': 0.6})

    square_vectors = square_quad.build_shape()
    rect_vectors = rect_quad.build_shape()

    # Should produce identical results
    assert len(square_vectors) == len(rect_vectors)
    for i in range(len(square_vectors)):
      assert abs(square_vectors[i].x - rect_vectors[i].x) < 1e-10
      assert abs(square_vectors[i].y - rect_vectors[i].y) < 1e-10

  def test_quadrilateral_delegation_to_geo_util(self):
    """Test that static methods properly delegate to GeoUtil."""
    # Test dimension validation delegation
    with pytest.raises(ValueError, match='test must be in range'):
      Quadrilateral._validate_dimension(-0.5, 'test')

    # Test slant calculation delegations work without error
    slant_from_angle = Quadrilateral._calc_slant_from_angle(1.0, 45.0)
    assert abs(slant_from_angle - 1.0) < 1e-10

    slant_from_side = Quadrilateral._calc_slant_from_side(3.0, 5.0)
    assert abs(slant_from_side - 4.0) < 1e-10  # 3-4-5 triangle

    # Test point creation delegation
    coords = [(0.0, 0.0), (1.0, 1.0)]
    points = Quadrilateral._make_points(coords)
    assert len(points) == 2
    assert points[0].x == 0.0 and points[0].y == 0.0
