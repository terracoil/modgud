"""Tests for QuadShapeEnum."""

import pytest
from modgud.domain.enums import QuadShapeEnum


class TestQuadShapeEnum:
  """Test suite for QuadShapeEnum functionality."""

  def test_from_string_with_value(self):
    """Test from_string with valid values."""
    assert QuadShapeEnum.from_string('RECTANGLE') == QuadShapeEnum.RECTANGLE
    assert QuadShapeEnum.from_string('square') == QuadShapeEnum.SQUARE
    assert QuadShapeEnum.from_string('Kite') == QuadShapeEnum.KITE

  def test_from_string_uses_default_behavior(self):
    """Test that empty/None values return first enum (RECTANGLE) by default."""
    # QuadShapeEnum doesn't override _get_default_value, so it uses the default
    # implementation which returns the first enum name
    assert QuadShapeEnum.from_string('') == QuadShapeEnum.RECTANGLE
    assert QuadShapeEnum.from_string(None) == QuadShapeEnum.RECTANGLE
    assert QuadShapeEnum._get_default_value() == QuadShapeEnum.RECTANGLE

  def test_from_string_invalid(self):
    """Test from_string with invalid values raises ValueError."""
    with pytest.raises(ValueError, match='is not a valid key for QuadShapeEnum'):
      QuadShapeEnum.from_string('INVALID_SHAPE')

  def test_parse_sides_string(self):
    """Test parse_sides_string with multiple shapes."""
    result = QuadShapeEnum.parse_sides_string('RECTANGLE,square KITE')
    assert result == [
      QuadShapeEnum.RECTANGLE,
      QuadShapeEnum.SQUARE,
      QuadShapeEnum.KITE,
    ]

  def test_enum_order(self):
    """Verify the order of enum values (important for default behavior)."""
    # Get all enum values in definition order
    enum_values = list(QuadShapeEnum)

    # Verify RECTANGLE is first (making it the default)
    assert enum_values[0] == QuadShapeEnum.RECTANGLE

    # Verify the expected order
    expected_order = [
      QuadShapeEnum.RECTANGLE,
      QuadShapeEnum.SQUARE,
      QuadShapeEnum.PARALLELOGRAM,
      QuadShapeEnum.RHOMBUS,
      QuadShapeEnum.RIGHTANGLE_TRAPEZOID,
      QuadShapeEnum.GENERAL_TRAPEZOID,
      QuadShapeEnum.ISOSCELES_TRAPEZOID,
      QuadShapeEnum.KITE,
    ]
    assert enum_values == expected_order
