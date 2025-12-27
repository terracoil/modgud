"""Tests for GeoUtil geometric utility functions."""

import math

import pytest
from modgud.api.geometry import GeoUtil, Vector


class TestGeoUtil:
  """Test suite for GeoUtil utility functions."""

  def test_validate_dimension_valid_exclusive_min(self):
    """Test dimension validation with exclusive minimum (default behavior)."""
    # Should pass - value within (0, 1]
    GeoUtil.validate_dimension(0.5, 'test_value')
    GeoUtil.validate_dimension(1.0, 'test_value')

  def test_validate_dimension_valid_inclusive_min(self):
    """Test dimension validation with inclusive minimum."""
    # Should pass - value within [0, 1]
    GeoUtil.validate_dimension(0.0, 'test_value', exclusive_min=False)
    GeoUtil.validate_dimension(0.5, 'test_value', exclusive_min=False)

  def test_validate_dimension_invalid_exclusive_min(self):
    """Test dimension validation failure with exclusive minimum."""
    with pytest.raises(ValueError, match='test_value must be in range \\(0.0, 1.0\\]'):
      GeoUtil.validate_dimension(0.0, 'test_value')  # exclusive_min=True by default

  def test_validate_dimension_invalid_inclusive_min(self):
    """Test dimension validation failure with inclusive minimum."""
    with pytest.raises(ValueError, match='test_value must be in range \\[0.0, 1.0\\]'):
      GeoUtil.validate_dimension(-0.1, 'test_value', exclusive_min=False)

  def test_validate_dimension_invalid_max(self):
    """Test dimension validation failure exceeding maximum."""
    with pytest.raises(ValueError, match='test_value must be in range \\(0.0, 1.0\\]'):
      GeoUtil.validate_dimension(1.1, 'test_value')

  def test_calc_slant_from_angle_valid(self):
    """Test slant calculation from valid angles."""
    # 45 degrees should give h/tan(45) = h/1 = h
    result = GeoUtil.calc_slant_from_angle(1.0, 45.0)
    assert abs(result - 1.0) < 1e-10

    # 30 degrees: tan(30) = 1/sqrt(3), so slant = h*sqrt(3)
    result = GeoUtil.calc_slant_from_angle(1.0, 30.0)
    expected = 1.0 / math.tan(math.radians(30.0))
    assert abs(result - expected) < 1e-10

  def test_calc_slant_from_angle_invalid(self):
    """Test slant calculation with invalid angles."""
    with pytest.raises(ValueError, match='Angle must be in range \\(0, 180\\) degrees'):
      GeoUtil.calc_slant_from_angle(1.0, 0.0)

    with pytest.raises(ValueError, match='Angle must be in range \\(0, 180\\) degrees'):
      GeoUtil.calc_slant_from_angle(1.0, 180.0)

    with pytest.raises(ValueError, match='Angle must be in range \\(0, 180\\) degrees'):
      GeoUtil.calc_slant_from_angle(1.0, -30.0)

  def test_calc_slant_from_side_valid(self):
    """Test slant calculation from side length (Pythagorean theorem)."""
    # 3-4-5 triangle: side=5, height=4, slant should be 3
    result = GeoUtil.calc_slant_from_side(4.0, 5.0)
    assert abs(result - 3.0) < 1e-10

    # Right triangle: side=hypotenuse=sqrt(2), height=1, slant should be 1
    result = GeoUtil.calc_slant_from_side(1.0, math.sqrt(2))
    assert abs(result - 1.0) < 1e-10

  def test_calc_slant_from_side_invalid(self):
    """Test slant calculation with invalid side length."""
    with pytest.raises(ValueError, match='Side length \\(2.0\\) must be >= height \\(3.0\\)'):
      GeoUtil.calc_slant_from_side(3.0, 2.0)

  def test_make_points_basic(self):
    """Test conversion of coordinate tuples to VectorPort objects."""
    coords = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
    vectors = GeoUtil.make_points(coords)

    assert len(vectors) == 4
    assert all(hasattr(v, 'x') and hasattr(v, 'y') for v in vectors)
    assert vectors[0].x == 0.0 and vectors[0].y == 0.0
    assert vectors[1].x == 1.0 and vectors[1].y == 0.0
    assert vectors[2].x == 1.0 and vectors[2].y == 1.0
    assert vectors[3].x == 0.0 and vectors[3].y == 1.0

  def test_make_points_empty(self):
    """Test make_points with empty coordinate list."""
    vectors = GeoUtil.make_points([])
    assert len(vectors) == 0

  def test_distance_basic(self):
    """Test distance calculation between two points."""
    p1 = Vector(0.0, 0.0)
    p2 = Vector(3.0, 4.0)

    distance = GeoUtil.distance(p1, p2)
    assert abs(distance - 5.0) < 1e-10  # 3-4-5 triangle

  def test_distance_same_point(self):
    """Test distance calculation between identical points."""
    p1 = Vector(2.5, 3.7)
    p2 = Vector(2.5, 3.7)

    distance = GeoUtil.distance(p1, p2)
    assert abs(distance) < 1e-10

  def test_distance_negative_coordinates(self):
    """Test distance calculation with negative coordinates."""
    p1 = Vector(-2.0, -3.0)
    p2 = Vector(1.0, 1.0)

    # Distance should be sqrt((1-(-2))^2 + (1-(-3))^2) = sqrt(9+16) = 5
    distance = GeoUtil.distance(p1, p2)
    assert abs(distance - 5.0) < 1e-10

  def test_polygon_area_rectangle(self):
    """Test polygon area calculation for a rectangle."""
    # 4x3 rectangle
    vertices = [Vector(0.0, 0.0), Vector(4.0, 0.0), Vector(4.0, 3.0), Vector(0.0, 3.0)]

    area = GeoUtil.polygon_area(vertices)
    assert abs(area - 12.0) < 1e-10

  def test_polygon_area_triangle(self):
    """Test polygon area calculation for a triangle."""
    # Right triangle with base=4, height=3, area should be 6
    vertices = [Vector(0.0, 0.0), Vector(4.0, 0.0), Vector(0.0, 3.0)]

    area = GeoUtil.polygon_area(vertices)
    assert abs(area - 6.0) < 1e-10

  def test_polygon_area_clockwise_vs_counterclockwise(self):
    """Test that polygon area is same regardless of vertex order."""
    vertices_ccw = [Vector(0.0, 0.0), Vector(2.0, 0.0), Vector(2.0, 2.0), Vector(0.0, 2.0)]

    vertices_cw = [Vector(0.0, 0.0), Vector(0.0, 2.0), Vector(2.0, 2.0), Vector(2.0, 0.0)]

    area_ccw = GeoUtil.polygon_area(vertices_ccw)
    area_cw = GeoUtil.polygon_area(vertices_cw)

    # Both should give same area (absolute value)
    assert abs(area_ccw - area_cw) < 1e-10
    assert abs(area_ccw - 4.0) < 1e-10

  def test_polygon_area_invalid_vertices(self):
    """Test polygon area with insufficient vertices."""
    with pytest.raises(ValueError, match='Polygon must have at least 3 vertices'):
      GeoUtil.polygon_area([Vector(0.0, 0.0)])

    with pytest.raises(ValueError, match='Polygon must have at least 3 vertices'):
      GeoUtil.polygon_area([Vector(0.0, 0.0), Vector(1.0, 0.0)])

  def test_polygon_perimeter_rectangle(self):
    """Test polygon perimeter calculation for a rectangle."""
    # 4x3 rectangle, perimeter should be 2*(4+3) = 14
    vertices = [Vector(0.0, 0.0), Vector(4.0, 0.0), Vector(4.0, 3.0), Vector(0.0, 3.0)]

    perimeter = GeoUtil.polygon_perimeter(vertices)
    assert abs(perimeter - 14.0) < 1e-10

  def test_polygon_perimeter_triangle(self):
    """Test polygon perimeter calculation for a 3-4-5 right triangle."""
    vertices = [
      Vector(0.0, 0.0),
      Vector(3.0, 0.0),  # base = 3
      Vector(0.0, 4.0),  # height = 4, hypotenuse = 5
    ]

    perimeter = GeoUtil.polygon_perimeter(vertices)
    expected = 3.0 + 4.0 + 5.0  # 3-4-5 triangle
    assert abs(perimeter - expected) < 1e-10

  def test_polygon_perimeter_invalid_vertices(self):
    """Test polygon perimeter with insufficient vertices."""
    with pytest.raises(ValueError, match='Polygon must have at least 2 vertices'):
      GeoUtil.polygon_perimeter([Vector(0.0, 0.0)])

  def test_degrees_to_radians(self):
    """Test degree to radian conversion."""
    assert abs(GeoUtil.degrees_to_radians(0.0) - 0.0) < 1e-10
    assert abs(GeoUtil.degrees_to_radians(90.0) - math.pi / 2) < 1e-10
    assert abs(GeoUtil.degrees_to_radians(180.0) - math.pi) < 1e-10
    assert abs(GeoUtil.degrees_to_radians(360.0) - 2 * math.pi) < 1e-10

  def test_radians_to_degrees(self):
    """Test radian to degree conversion."""
    assert abs(GeoUtil.radians_to_degrees(0.0) - 0.0) < 1e-10
    assert abs(GeoUtil.radians_to_degrees(math.pi / 2) - 90.0) < 1e-10
    assert abs(GeoUtil.radians_to_degrees(math.pi) - 180.0) < 1e-10
    assert abs(GeoUtil.radians_to_degrees(2 * math.pi) - 360.0) < 1e-10

  def test_angle_conversion_roundtrip(self):
    """Test that degree<->radian conversion is reversible."""
    original_degrees = 45.0
    radians = GeoUtil.degrees_to_radians(original_degrees)
    back_to_degrees = GeoUtil.radians_to_degrees(radians)

    assert abs(original_degrees - back_to_degrees) < 1e-10
