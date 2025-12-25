"""Tests for the StackableTrapezoid geometry generator."""

import pytest
from modgud.api.geometry import StackableTrapezoid, migrate_shape_result

from tests.test_shape_utils import ShapeTestUtils


class TestStackableTrapezoid:
  """Test cases for StackableTrapezoid."""

  def test_basic_trapezoid(self):
    """Test basic trapezoid generation with default parameters."""
    st = StackableTrapezoid()
    result = st.build_shape()

    # Verify new return structure (Sequence[VectorPort])
    ShapeTestUtils.assert_valid_vector_sequence(result)

    # Test backward compatibility
    legacy_result = migrate_shape_result(result)
    assert isinstance(legacy_result, dict)
    assert 'shape' in legacy_result
    assert isinstance(legacy_result['shape'], list)
    assert len(legacy_result['shape']) > 0

    # Check that it's a valid SVG path in legacy format
    svg_lines = legacy_result['shape']
    assert any('<path' in line for line in svg_lines)
    assert any('<close/>' in line for line in svg_lines)

  def test_custom_parameters(self):
    """Test trapezoid with custom angle and stackable percentage."""
    st = StackableTrapezoid(angle=75, notch_height=0.3, width=80, height=60)
    result = st.build_shape()

    # Verify new return structure
    ShapeTestUtils.assert_valid_vector_sequence(result)

    # Test backward compatibility
    legacy_result = migrate_shape_result(result)
    assert 'shape' in legacy_result
    svg_lines = legacy_result['shape']

    # Verify SVG structure is valid
    assert any('<path' in line for line in svg_lines)
    assert any('<move' in line for line in svg_lines)

    # Verify scaling was applied (check for coordinates that reflect dimensions)
    all_lines = ' '.join(svg_lines)
    assert '80.0' in all_lines or '60.0' in all_lines

  def test_inverted_trapezoid(self):
    """Test inverted trapezoid generation."""
    st = StackableTrapezoid(invert=True)
    result = st.build_shape()

    # Verify new return structure
    ShapeTestUtils.assert_valid_vector_sequence(result)

    # Test backward compatibility
    legacy_result = migrate_shape_result(result)
    assert 'shape' in legacy_result
    svg_lines = legacy_result['shape']

    # Inverted trapezoid should start at top left (0, 0)
    assert any('<move x="0.0" y="0.0"' in line for line in svg_lines)

  def test_parameter_validation(self):
    """Test that invalid parameters raise appropriate errors."""
    # Test angle validation - errors occur at construction time
    with pytest.raises(ValueError, match='angle should be between 70° and 85°'):
      StackableTrapezoid(angle=60)

    with pytest.raises(ValueError, match='angle should be between 70° and 85°'):
      StackableTrapezoid(angle=90)

    # Test notch_height validation
    with pytest.raises(ValueError, match='notch_height should be between 10% and 40%'):
      StackableTrapezoid(notch_height=0.05)

    with pytest.raises(ValueError, match='notch_height should be between 10% and 40%'):
      StackableTrapezoid(notch_height=0.6)

  def test_valid_angle_range(self):
    """Test trapezoid with valid angle range."""
    # Test minimum valid angle
    st_min = StackableTrapezoid(angle=70)
    result_min = st_min.build_shape()
    ShapeTestUtils.assert_valid_vector_sequence(result_min)

    # Test maximum valid angle
    st_max = StackableTrapezoid(angle=85)
    result_max = st_max.build_shape()
    ShapeTestUtils.assert_valid_vector_sequence(result_max)

    # Test middle range angle
    st_mid = StackableTrapezoid(angle=77)
    result_mid = st_mid.build_shape()
    ShapeTestUtils.assert_valid_vector_sequence(result_mid)

  def test_nesting_positions(self):
    """Test the nesting positions method."""
    st = StackableTrapezoid()
    result = st.calculate_nesting_positions(count=3)

    # Result should be a list of vector sequences
    assert isinstance(result, list)
    assert len(result) == 3

    # Each shape should be a sequence of vectors
    for shape in result:
      ShapeTestUtils.assert_valid_vector_sequence(shape)

    # Test backward compatibility for each shape
    for i, shape in enumerate(result):
      legacy_dict = migrate_shape_result(shape, f'shape_{i}')
      assert isinstance(legacy_dict, dict)
      assert f'shape_{i}' in legacy_dict

  def test_nesting_positions_validation(self):
    """Test nesting positions parameter validation."""
    st = StackableTrapezoid()

    with pytest.raises(ValueError, match='count should be between 2 and 5'):
      st.calculate_nesting_positions(count=1)

    with pytest.raises(ValueError, match='count should be between 2 and 5'):
      st.calculate_nesting_positions(count=6)

  def test_stackability(self):
    """Test that generated trapezoids have proper notch dimensions for stacking."""
    st = StackableTrapezoid(angle=75, notch_height=0.2)
    result = st.build_shape()

    # Verify vector sequence structure
    ShapeTestUtils.assert_valid_vector_sequence(
      result, min_length=8
    )  # Should have at least 8 points for trapezoid with notch

    # Test backward compatibility to check SVG structure
    legacy_result = migrate_shape_result(result)
    svg_lines = legacy_result['shape']

    # Check that notch-related segments are present
    assert any('notch' in line.lower() for line in svg_lines)

    # The trapezoid should have proper closure
    assert any('<path' in line for line in svg_lines)
    assert any('<close/>' in line for line in svg_lines)

  def test_dataclass_immutability(self):
    """Test that StackableTrapezoid is immutable (frozen=True)."""
    st = StackableTrapezoid(angle=75, notch_height=0.25, width=120, height=80)

    # Test that we can't modify attributes
    ShapeTestUtils.assert_dataclass_immutability(st, 'angle', 80)
    ShapeTestUtils.assert_dataclass_immutability(st, 'notch_height', 0.3)
    ShapeTestUtils.assert_dataclass_immutability(st, 'width', 150)
    ShapeTestUtils.assert_dataclass_immutability(st, 'invert', True)

  def test_constructor_parameters(self):
    """Test that all parameters work in constructor."""
    st = StackableTrapezoid(
      angle=80,
      notch_height=0.35,
      width=150,
      height=120,
      invert=True,
    )

    # Verify parameters are set correctly
    assert st.angle == 80
    assert st.notch_height == 0.35
    assert st.width == 150
    assert st.height == 120
    assert st.invert == True

    # Verify build_shape works
    result = st.build_shape()
    ShapeTestUtils.assert_valid_vector_sequence(result)

  def test_validation_in_constructor(self):
    """Test that validation happens in constructor (__post_init__)."""
    # Invalid angle should fail at construction
    with pytest.raises(ValueError, match='angle should be between 70° and 85°'):
      StackableTrapezoid(angle=65)

    with pytest.raises(ValueError, match='angle should be between 70° and 85°'):
      StackableTrapezoid(angle=90)

    # Invalid notch_height should fail at construction
    with pytest.raises(ValueError, match='notch_height should be between 10% and 40%'):
      StackableTrapezoid(notch_height=0.05)

    with pytest.raises(ValueError, match='notch_height should be between 10% and 40%'):
      StackableTrapezoid(notch_height=0.5)

  def test_return_type_is_vector_sequence(self):
    """Test that build_shape returns Sequence[VectorPort], not SVG dict."""
    st = StackableTrapezoid(angle=75)

    result = st.build_shape()

    # Should be a sequence of vectors
    ShapeTestUtils.assert_valid_vector_sequence(result)

    # Should NOT be the old dictionary format
    assert not isinstance(result, dict)
    assert not hasattr(result, 'keys')

  def test_backward_compatibility_conversion(self):
    """Test that results can be converted to legacy format."""
    st = StackableTrapezoid(angle=72, notch_height=0.15, width=80, height=60)

    vectors = st.build_shape()
    legacy_dict = ShapeTestUtils.assert_backward_compatibility(vectors)

    # Verify structure matches old format
    assert 'shape' in legacy_dict
    assert isinstance(legacy_dict['shape'], list)
    assert len(legacy_dict['shape']) > 0

    # Verify SVG commands
    svg_commands = legacy_dict['shape']
    assert any('<path' in cmd for cmd in svg_commands)
    assert any('<move' in cmd for cmd in svg_commands)
    assert any('<close/>' in cmd for cmd in svg_commands)

  def test_different_parameters_produce_different_results(self):
    """Test that different parameters produce different shapes."""
    st1 = StackableTrapezoid(angle=72, notch_height=0.2)
    st2 = StackableTrapezoid(angle=78, notch_height=0.2)
    st3 = StackableTrapezoid(angle=72, notch_height=0.3)
    st4 = StackableTrapezoid(angle=72, notch_height=0.2, invert=True)

    result1 = st1.build_shape()
    result2 = st2.build_shape()
    result3 = st3.build_shape()
    result4 = st4.build_shape()

    # Different angles should produce different results
    assert result1 != result2

    # Different notch heights should produce different results
    assert result1 != result3

    # Different invert settings should produce different results
    assert result1 != result4

  def test_extreme_valid_parameters(self):
    """Test with extreme but valid parameter values."""
    # Minimum valid parameters
    st_min = StackableTrapezoid(angle=70, notch_height=0.1, width=10, height=10)
    result_min = st_min.build_shape()
    ShapeTestUtils.assert_valid_vector_sequence(result_min)

    # Maximum valid parameters
    st_max = StackableTrapezoid(angle=85, notch_height=0.4, width=1000, height=1000)
    result_max = st_max.build_shape()
    ShapeTestUtils.assert_valid_vector_sequence(result_max)

  def test_nesting_positions_offset_calculation(self):
    """Test that nesting positions have proper vertical offsets."""
    st = StackableTrapezoid(angle=75, notch_height=0.25, height=100)
    positions = st.calculate_nesting_positions(count=3)

    # Should have 3 shapes
    assert len(positions) == 3

    # Each position should be valid
    for i, shape in enumerate(positions):
      ShapeTestUtils.assert_valid_vector_sequence(shape)

    # First shape should be at original position (y=0 at top)
    first_shape = positions[0]
    # Last shape should be offset (y values should be different)
    last_shape = positions[2]

    # The shapes should have different y coordinates due to vertical offset
    first_y_values = [v.y for v in first_shape]
    last_y_values = [v.y for v in last_shape]
    assert first_y_values != last_y_values
