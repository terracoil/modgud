"""Comprehensive tests for all shape classes in the refactored architecture."""

from __future__ import annotations

import math

import pytest
from modgud.domain.enums import OrdinalEnum
from modgud.util.geo import SimplexNoise
from modgud.util.geo.shapes import (
  Kite,
  Parallelogram,
  Rectangle,
  Rhombus,
  ShapeFactory,
  Square,
  Trapezoid,
)


class TestSquare:
  """Test suite for Square shape."""

  def test_square_basic_creation(self):
    """Test basic square creation with valid parameters."""
    square = Square(side=0.5)
    vertices = square.build_shape()

    # Should have 4 vertices
    assert len(vertices) == 4

    # Check coordinates are correct
    assert vertices[0].x == 0 and vertices[0].y == 0  # bottom-left
    assert vertices[1].x == 0.5 and vertices[1].y == 0  # bottom-right
    assert vertices[2].x == 0.5 and vertices[2].y == 0.5  # top-right
    assert vertices[3].x == 0 and vertices[3].y == 0.5  # top-left

  def test_square_edge_angles(self):
    """Test that square edges are all 0 or 90 degrees."""
    square = Square(side=0.5)

    # All edges should be horizontal or vertical
    assert square.get_edge_angle(0) == 0  # Bottom edge (horizontal)
    assert abs(square.get_edge_angle(1) - math.pi / 2) < 1e-6  # Right edge (vertical)
    assert square.get_edge_angle(2) == 0  # Top edge (horizontal)
    assert abs(square.get_edge_angle(3) - math.pi / 2) < 1e-6  # Left edge (vertical)

  def test_square_with_notches(self):
    """Test square with notches on multiple sides."""
    square = Square(
      side=1.0, notch_sides=[OrdinalEnum.SOUTH, OrdinalEnum.NORTH], notch_size=0.2, notch_depth=0.1
    )
    vertices = square.build_shape()

    # Should have more than 4 vertices due to notches
    assert len(vertices) > 4

  def test_square_with_torn_edges(self):
    """Test square with torn edges."""
    noise = SimplexNoise(42)
    square = Square(
      side=1.0, torn_sides=[OrdinalEnum.EAST, OrdinalEnum.WEST], noise=noise, noise_amplitude=5.0
    )
    vertices = square.build_shape()

    # Should have many vertices due to torn edges
    assert len(vertices) > 20

  def test_square_invalid_parameters(self):
    """Test square validation with invalid parameters."""
    # Negative side
    with pytest.raises(ValueError, match='Side length'):
      Square(side=-0.5)

    # Zero side
    with pytest.raises(ValueError, match='Side length'):
      Square(side=0)

    # Too large
    with pytest.raises(ValueError, match='Side length'):
      Square(side=1.5)


class TestRectangle:
  """Test suite for Rectangle shape."""

  def test_rectangle_basic_creation(self):
    """Test basic rectangle creation."""
    rect = Rectangle(width=0.8, height=0.6)
    vertices = rect.build_shape()

    assert len(vertices) == 4
    assert vertices[0].x == 0 and vertices[0].y == 0
    assert vertices[1].x == 0.8 and vertices[1].y == 0
    assert vertices[2].x == 0.8 and vertices[2].y == 0.6
    assert vertices[3].x == 0 and vertices[3].y == 0.6

  def test_rectangle_edge_angles(self):
    """Test rectangle edge angles."""
    rect = Rectangle(width=0.8, height=0.6)

    assert rect.get_edge_angle(0) == 0  # Bottom
    assert abs(rect.get_edge_angle(1) - math.pi / 2) < 1e-6  # Right
    assert rect.get_edge_angle(2) == 0  # Top
    assert abs(rect.get_edge_angle(3) - math.pi / 2) < 1e-6  # Left

  def test_rectangle_with_decorations(self):
    """Test rectangle with both torn edges and notches."""
    noise = SimplexNoise(42)
    rect = Rectangle(
      width=1.0,
      height=0.5,
      torn_sides=[OrdinalEnum.SOUTH],
      notch_sides=[OrdinalEnum.SOUTH],  # Same side has both
      notch_size=0.15,
      notch_depth=0.2,
      noise=noise,
    )
    vertices = rect.build_shape()

    # Should have complex shape due to torn notch
    assert len(vertices) > 10

  def test_rectangle_validation(self):
    """Test rectangle parameter validation."""
    # Invalid width
    with pytest.raises(ValueError, match='Width'):
      Rectangle(width=0, height=0.5)

    # Invalid height
    with pytest.raises(ValueError, match='Height'):
      Rectangle(width=0.5, height=-0.1)


class TestParallelogram:
  """Test suite for Parallelogram shape."""

  def test_parallelogram_with_angle(self):
    """Test parallelogram creation with angle parameter."""
    para = Parallelogram(width=1.0, height=0.6, angle=math.pi / 3)  # 60 degrees
    vertices = para.build_shape()

    assert len(vertices) == 4
    # Verify it's slanted (not a rectangle)
    assert vertices[2].x != vertices[1].x
    assert vertices[3].x != vertices[0].x

  def test_parallelogram_with_slant(self):
    """Test parallelogram creation with slant parameter."""
    # Note: angle is still required, slant is optional and overrides angle calculation
    para = Parallelogram(width=1.0, height=0.6, angle=math.pi / 4, slant=0.3)
    vertices = para.build_shape()

    assert len(vertices) == 4
    # Check slant is applied correctly when provided
    # Note: the exact coordinates depend on the implementation details

  def test_parallelogram_edge_angles(self):
    """Test parallelogram edge angles are consistent."""
    para = Parallelogram(width=1.0, height=0.6, angle=math.pi / 4)

    bottom_angle = para.get_edge_angle(0)
    top_angle = para.get_edge_angle(2)

    # Bottom and top should be parallel (same angle)
    assert abs(bottom_angle - top_angle) < 1e-6

  def test_parallelogram_validation(self):
    """Test parallelogram parameter validation."""
    # Invalid angle (too small)
    with pytest.raises(ValueError, match='Angle'):
      Parallelogram(width=1.0, height=0.6, angle=0.05)

    # Invalid angle (too large)
    with pytest.raises(ValueError, match='Angle'):
      Parallelogram(width=1.0, height=0.6, angle=math.pi - 0.05)


class TestRhombus:
  """Test suite for Rhombus shape."""

  def test_rhombus_basic(self):
    """Test basic rhombus creation."""
    rhombus = Rhombus(side=0.7, angle=math.pi / 3)
    vertices = rhombus.build_shape()

    assert len(vertices) == 4

    # All sides should be equal length
    side1 = math.sqrt((vertices[1].x - vertices[0].x) ** 2 + (vertices[1].y - vertices[0].y) ** 2)
    side2 = math.sqrt((vertices[2].x - vertices[1].x) ** 2 + (vertices[2].y - vertices[1].y) ** 2)
    side3 = math.sqrt((vertices[3].x - vertices[2].x) ** 2 + (vertices[3].y - vertices[2].y) ** 2)
    side4 = math.sqrt((vertices[0].x - vertices[3].x) ** 2 + (vertices[0].y - vertices[3].y) ** 2)

    assert abs(side1 - 0.7) < 1e-6
    assert abs(side2 - 0.7) < 1e-6
    assert abs(side3 - 0.7) < 1e-6
    assert abs(side4 - 0.7) < 1e-6

  def test_rhombus_with_notches(self):
    """Test rhombus with notches."""
    rhombus = Rhombus(
      side=0.8,
      angle=math.pi / 2,  # Square rhombus
      notch_sides=[OrdinalEnum.EAST, OrdinalEnum.WEST],
      notch_size=0.1,
      notch_depth=0.15,
    )
    vertices = rhombus.build_shape()

    assert len(vertices) > 4


class TestKite:
  """Test suite for Kite shape."""

  def test_kite_basic(self):
    """Test basic kite creation."""
    kite = Kite(diagonal1=1.0, diagonal2=0.6)
    vertices = kite.build_shape()

    assert len(vertices) == 4

    # Kite vertices are normalized to fit in unit square
    # Check that we have 4 distinct vertices
    x_coords = [v.x for v in vertices]
    y_coords = [v.y for v in vertices]

    # All coordinates should be within [0, 1] after normalization
    assert all(0 <= x <= 1 for x in x_coords)
    assert all(0 <= y <= 1 for y in y_coords)

    # Should have distinct vertices
    assert len(set(zip(x_coords, y_coords, strict=False))) == 4

  def test_kite_edge_angles(self):
    """Test kite edge angles."""
    kite = Kite(diagonal1=1.0, diagonal2=0.6)

    # Get all edge angles
    angles = [kite.get_edge_angle(i) for i in range(4)]

    # All angles should be valid
    for angle in angles:
      assert not math.isnan(angle) and not math.isinf(angle)

  def test_kite_with_torn_edges(self):
    """Test kite with torn edges."""
    noise = SimplexNoise(123)
    kite = Kite(
      diagonal1=0.8,
      diagonal2=0.8,
      torn_sides=[OrdinalEnum.NORTH, OrdinalEnum.SOUTH],
      noise=noise,
      noise_amplitude=3.0,
    )
    vertices = kite.build_shape()

    assert len(vertices) > 20


class TestShapeFactory:
  """Test suite for ShapeFactory."""

  def test_create_square(self):
    """Test creating square directly."""
    shape = Square(side=0.5)
    assert isinstance(shape, Square)
    vertices = shape.build_shape()
    assert len(vertices) == 4

  def test_create_rectangle(self):
    """Test creating rectangle directly."""
    shape = Rectangle(width=0.8, height=0.6)
    assert isinstance(shape, Rectangle)

  def test_create_trapezoid_variants(self):
    """Test creating different trapezoid variants directly."""
    # Isosceles
    iso = Trapezoid(w1=1.0, w2=0.6, h=0.8)
    assert isinstance(iso, Trapezoid)

    # Right angle
    right = Trapezoid(w1=1.0, w2=0.6, h=0.8, side_left=0.8)
    assert isinstance(right, Trapezoid)

    # General
    general = Trapezoid(w1=1.0, w2=0.6, h=0.8, side_left=1.2)
    assert isinstance(general, Trapezoid)

  def test_create_shape_api(self):
    """Test string-based API."""
    square = ShapeFactory.create_shape('square', side=0.5)
    assert isinstance(square, Square)

    rect = ShapeFactory.create_shape('rectangle', width=0.8, height=0.6)
    assert isinstance(rect, Rectangle)

    trap = ShapeFactory.create_shape('trapezoid', w1=1.0, w2=0.6, h=0.8)
    assert isinstance(trap, Trapezoid)

  def test_factory_error_handling(self):
    """Test factory error conditions."""
    # Invalid shape name
    with pytest.raises(ValueError, match='Unknown shape type'):
      ShapeFactory.create_shape('hexagon', side=1.0)

  def test_direct_shape_creation(self):
    """Test direct shape creation with various parameters."""
    # Rectangle
    rect = Rectangle(width=0.8, height=0.6)
    assert isinstance(rect, Rectangle)

    # Kite
    kite = Kite(diagonal1=1.0, diagonal2=0.6)
    assert isinstance(kite, Kite)

  def test_list_available_shapes(self):
    """Test listing available shapes."""
    shapes = ShapeFactory.list_available_shapes()
    assert 'square' in shapes
    assert 'rectangle' in shapes
    assert 'trapezoid' in shapes
    assert 'parallelogram' in shapes
    assert 'rhombus' in shapes
    assert 'kite' in shapes
    assert len(shapes) == 6

  def test_get_shape_parameters(self):
    """Test getting parameter info for shapes."""
    square_params = ShapeFactory.get_shape_parameters('square')
    assert 'side' in square_params

    trap_params = ShapeFactory.get_shape_parameters('trapezoid')
    assert 'w1' in trap_params
    assert 'w2' in trap_params
    assert 'h' in trap_params

    # Invalid shape
    with pytest.raises(ValueError, match='Unknown shape type'):
      ShapeFactory.get_shape_parameters('octagon')


class TestEdgeCases:
  """Test edge cases and complex scenarios."""

  def test_very_small_shapes(self):
    """Test shapes with very small dimensions."""
    small_square = Square(side=0.01)
    vertices = small_square.build_shape()
    assert len(vertices) == 4

    small_rect = Rectangle(width=0.01, height=0.01)
    vertices = small_rect.build_shape()
    assert len(vertices) == 4

  def test_maximum_size_shapes(self):
    """Test shapes at maximum allowed size."""
    max_square = Square(side=1.0)
    vertices = max_square.build_shape()
    assert len(vertices) == 4

    max_trap = Trapezoid(w1=1.0, w2=1.0, h=1.0)
    vertices = max_trap.build_shape()
    assert len(vertices) == 4

  def test_complex_decorations(self):
    """Test shapes with multiple complex decorations."""
    noise = SimplexNoise(999)

    # Rectangle with all sides torn and notched
    complex_rect = Rectangle(
      width=0.8,
      height=0.6,
      torn_sides=[OrdinalEnum.NORTH, OrdinalEnum.SOUTH, OrdinalEnum.EAST, OrdinalEnum.WEST],
      notch_sides=[OrdinalEnum.NORTH, OrdinalEnum.SOUTH],
      notch_size=0.1,
      notch_depth=0.2,
      noise=noise,
      noise_amplitude=5.0,
      noise_segments=50,
    )
    vertices = complex_rect.build_shape()

    # Should have very complex shape
    assert len(vertices) > 100
