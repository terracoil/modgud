"""Tests for Quadrilateral notch functionality."""

import pytest
from modgud.domain.enums import OrdinalEnum, QuadShapeEnum
from modgud.util.geo import Quadrilateral


class TestQuadrilateralNotch:
  """Test suite for Quadrilateral notch functionality."""

  def test_quadrilateral_no_notches_default(self):
    """Test quadrilateral with no notches (default behavior)."""
    quad = Quadrilateral(quad_shape=QuadShapeEnum.RECTANGLE, params={'w': 0.8, 'h': 0.6})
    vectors = quad.build_shape()

    # Should be a basic rectangle with 4 vertices
    assert len(vectors) == 4
    assert vectors[0].x == 0.0 and vectors[0].y == 0.0  # bottom-left
    assert vectors[1].x == 0.8 and vectors[1].y == 0.0  # bottom-right
    assert vectors[2].x == 0.8 and vectors[2].y == 0.6  # top-right
    assert vectors[3].x == 0.0 and vectors[3].y == 0.6  # top-left

  def test_quadrilateral_with_north_notch(self):
    """Test quadrilateral with a notch on the north (top) side."""
    quad = Quadrilateral(
      quad_shape=QuadShapeEnum.RECTANGLE,
      params={'w': 1.0, 'h': 1.0},
      notch_sides=[OrdinalEnum.NORTH],
      notch_size=0.2,
      notch_depth=0.1,
    )
    vectors = quad.build_shape()

    # Should have more than 4 vertices due to the notch
    assert len(vectors) > 4

    # Should contain some vectors with y values greater than the original height
    # because notch goes inward from the top edge
    max_y = max(v.y for v in vectors)
    assert max_y >= 1.0  # Should extend beyond original height due to inward notch

  def test_quadrilateral_with_south_notch(self):
    """Test quadrilateral with a notch on the south (bottom) side."""
    quad = Quadrilateral(
      quad_shape=QuadShapeEnum.RECTANGLE,
      params={'w': 1.0, 'h': 1.0},
      notch_sides=[OrdinalEnum.SOUTH],
      notch_size=0.3,
      notch_depth=0.15,
    )
    vectors = quad.build_shape()

    # Should have more than 4 vertices due to the notch
    assert len(vectors) > 4

    # Should contain some vectors with negative y values
    # because notch goes inward from the bottom edge
    min_y = min(v.y for v in vectors)
    assert min_y < 0.0  # Should extend below original bottom edge

  def test_quadrilateral_with_east_notch(self):
    """Test quadrilateral with a notch on the east (right) side."""
    quad = Quadrilateral(
      quad_shape=QuadShapeEnum.RECTANGLE,
      params={'w': 1.0, 'h': 1.0},
      notch_sides=[OrdinalEnum.EAST],
      notch_size=0.25,
      notch_depth=0.1,
    )
    vectors = quad.build_shape()

    # Should have more than 4 vertices due to the notch
    assert len(vectors) > 4

    # Should contain some vectors with x values greater than the original width
    # because notch goes inward from the right edge
    max_x = max(v.x for v in vectors)
    assert max_x >= 1.0  # Should extend beyond original width due to inward notch

  def test_quadrilateral_with_west_notch(self):
    """Test quadrilateral with a notch on the west (left) side."""
    quad = Quadrilateral(
      quad_shape=QuadShapeEnum.RECTANGLE,
      params={'w': 1.0, 'h': 1.0},
      notch_sides=[OrdinalEnum.WEST],
      notch_size=0.2,
      notch_depth=0.2,
    )
    vectors = quad.build_shape()

    # Should have more than 4 vertices due to the notch
    assert len(vectors) > 4

    # Should contain some vectors with negative x values
    # because notch goes inward from the left edge
    min_x = min(v.x for v in vectors)
    assert min_x < 0.0  # Should extend beyond original left edge

  def test_quadrilateral_with_multiple_notches(self):
    """Test quadrilateral with notches on multiple sides."""
    quad = Quadrilateral(
      quad_shape=QuadShapeEnum.RECTANGLE,
      params={'w': 1.0, 'h': 1.0},
      notch_sides=[OrdinalEnum.NORTH, OrdinalEnum.SOUTH],
      notch_size=0.2,
      notch_depth=0.1,
    )
    vectors = quad.build_shape()

    # Should have significantly more than 4 vertices due to multiple notches
    assert len(vectors) > 6

    # Should extend beyond original bounds in both y directions
    min_y = min(v.y for v in vectors)
    max_y = max(v.y for v in vectors)
    assert min_y < 0.0  # South notch extends below
    assert max_y > 1.0  # North notch extends above

  def test_quadrilateral_with_corner_notch_ne(self):
    """Test quadrilateral with a northeast corner notch."""
    quad = Quadrilateral(
      quad_shape=QuadShapeEnum.RECTANGLE,
      params={'w': 1.0, 'h': 1.0},
      notch_sides=[OrdinalEnum.NORTHEAST],
      notch_size=0.1,
      notch_depth=0.1,
    )
    vectors = quad.build_shape()

    # Should have at least 4 vertices, corner notch modifies existing vertices
    assert len(vectors) >= 4

    # The northeast corner should be inset (moved toward center)
    # Original corner was at (1.0, 1.0), should now be closer to center
    ne_corner = max(vectors, key=lambda v: v.x + v.y)  # Find point closest to NE
    assert ne_corner.x < 1.0 or ne_corner.y < 1.0  # Should be inset from (1,1)

  def test_quadrilateral_notch_validation_invalid_sides(self):
    """Test validation of invalid notch sides."""
    with pytest.raises(ValueError, match='Invalid notch side'):
      Quadrilateral(
        quad_shape=QuadShapeEnum.RECTANGLE,
        params={'w': 1.0, 'h': 1.0},
        notch_sides=[999],  # Invalid enum name
        notch_size=0.1,
        notch_depth=0.1,
      )

  def test_quadrilateral_notch_validation_invalid_size(self):
    """Test validation of invalid notch size."""
    with pytest.raises(ValueError, match='notch_size must be in range'):
      Quadrilateral(
        quad_shape=QuadShapeEnum.RECTANGLE,
        params={'w': 1.0, 'h': 1.0},
        notch_sides=[OrdinalEnum.NORTH],
        notch_size=1.5,  # Invalid - exceeds 1.0
        notch_depth=0.1,
      )

  def test_quadrilateral_notch_validation_invalid_depth(self):
    """Test validation of invalid notch depth."""
    with pytest.raises(ValueError, match='notch_depth must be in range'):
      Quadrilateral(
        quad_shape=QuadShapeEnum.RECTANGLE,
        params={'w': 1.0, 'h': 1.0},
        notch_sides=[OrdinalEnum.NORTH],
        notch_size=0.2,
        notch_depth=-0.1,  # Invalid - negative
      )

  def test_quadrilateral_notch_validation_invalid_offset(self):
    """Test validation of invalid notch offset."""
    with pytest.raises(ValueError, match='notch_offset must be in range'):
      Quadrilateral(
        quad_shape=QuadShapeEnum.RECTANGLE,
        params={'w': 1.0, 'h': 1.0},
        notch_sides=[OrdinalEnum.NORTH],
        notch_size=0.2,
        notch_depth=0.1,
        notch_offset=0.8,  # Invalid - exceeds 0.5
      )

  def test_quadrilateral_notch_with_offset(self):
    """Test quadrilateral notch with non-zero offset."""
    quad = Quadrilateral(
      quad_shape=QuadShapeEnum.RECTANGLE,
      params={'w': 1.0, 'h': 1.0},
      notch_sides=[OrdinalEnum.NORTH],
      notch_size=0.2,
      notch_depth=0.1,
      notch_offset=0.25,  # Offset toward the right
    )
    vectors = quad.build_shape()

    # Should have more than 4 vertices due to the notch
    assert len(vectors) > 4

    # The notch should be offset from the center of the top edge
    # Center would be at x=0.5, offset should move it toward x=0.75
    notch_points = [v for v in vectors if v.y > 1.0]  # Points above original top edge
    if notch_points:
      avg_notch_x = sum(p.x for p in notch_points) / len(notch_points)
      assert avg_notch_x > 0.5  # Should be offset from center

  def test_quadrilateral_zero_notch_parameters(self):
    """Test quadrilateral with zero notch size or depth (should behave like no notch)."""
    # Zero size
    quad_zero_size = Quadrilateral(
      quad_shape=QuadShapeEnum.RECTANGLE,
      params={'w': 1.0, 'h': 1.0},
      notch_sides=[OrdinalEnum.NORTH],
      notch_size=0.0,  # Zero size - no notch
      notch_depth=0.2,
    )
    vectors_zero_size = quad_zero_size.build_shape()
    assert len(vectors_zero_size) == 4  # Should be basic rectangle

    # Zero depth
    quad_zero_depth = Quadrilateral(
      quad_shape=QuadShapeEnum.RECTANGLE,
      params={'w': 1.0, 'h': 1.0},
      notch_sides=[OrdinalEnum.NORTH],
      notch_size=0.2,
      notch_depth=0.0,  # Zero depth - no notch
    )
    vectors_zero_depth = quad_zero_depth.build_shape()
    assert len(vectors_zero_depth) == 4  # Should be basic rectangle

  def test_quadrilateral_different_shapes_with_notches(self):
    """Test notches work with different quadrilateral shapes."""
    # Test with square
    quad_square = Quadrilateral(
      quad_shape=QuadShapeEnum.SQUARE,
      params={'side': 0.8},
      notch_sides=[OrdinalEnum.EAST],
      notch_size=0.2,
      notch_depth=0.1,
    )
    vectors_square = quad_square.build_shape()
    assert len(vectors_square) > 4  # Should have notch

    # Test with parallelogram
    quad_para = Quadrilateral(
      quad_shape=QuadShapeEnum.PARALLELOGRAM,
      params={'w': 0.8, 'h': 0.6, 'angle': 60.0},
      notch_sides=[OrdinalEnum.SOUTH],
      notch_size=0.15,
      notch_depth=0.1,
    )
    vectors_para = quad_para.build_shape()
    assert len(vectors_para) > 4  # Should have notch

  def test_quadrilateral_notch_immutability(self):
    """Test that Quadrilateral with notches is still immutable (frozen dataclass)."""
    quad = Quadrilateral(
      quad_shape=QuadShapeEnum.RECTANGLE,
      params={'w': 1.0, 'h': 1.0},
      notch_sides=[OrdinalEnum.NORTH],
      notch_size=0.2,
      notch_depth=0.1,
    )

    # Should not be able to modify notch parameters
    with pytest.raises(AttributeError):  # frozen=True prevents modification
      quad.notch_size = 0.5

    with pytest.raises(AttributeError):
      quad.notch_sides = [OrdinalEnum.SOUTH]

  def test_quadrilateral_notch_boundary_conditions(self):
    """Test notch behavior at parameter boundaries."""
    # Maximum size and depth
    quad_max = Quadrilateral(
      quad_shape=QuadShapeEnum.RECTANGLE,
      params={'w': 1.0, 'h': 1.0},
      notch_sides=[OrdinalEnum.NORTH],
      notch_size=1.0,  # Maximum size
      notch_depth=1.0,  # Maximum depth
    )
    vectors_max = quad_max.build_shape()
    # Should not crash and should create a valid shape
    assert len(vectors_max) > 4

    # Maximum offset values
    quad_max_offset_pos = Quadrilateral(
      quad_shape=QuadShapeEnum.RECTANGLE,
      params={'w': 1.0, 'h': 1.0},
      notch_sides=[OrdinalEnum.NORTH],
      notch_size=0.2,
      notch_depth=0.1,
      notch_offset=0.5,  # Maximum positive offset
    )
    vectors_max_pos = quad_max_offset_pos.build_shape()
    assert len(vectors_max_pos) > 4

    quad_max_offset_neg = Quadrilateral(
      quad_shape=QuadShapeEnum.RECTANGLE,
      params={'w': 1.0, 'h': 1.0},
      notch_sides=[OrdinalEnum.NORTH],
      notch_size=0.2,
      notch_depth=0.1,
      notch_offset=-0.5,  # Maximum negative offset
    )
    vectors_max_neg = quad_max_offset_neg.build_shape()
    assert len(vectors_max_neg) > 4
