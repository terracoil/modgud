"""Tests for the StackableTrapezoid geometry generator."""

import pytest

from modgud.api.geometry import StackableTrapezoid


class TestStackableTrapezoid:
  """Test cases for StackableTrapezoid."""

  def test_basic_trapezoid(self):
    """Test basic trapezoid generation with default parameters."""
    st = StackableTrapezoid()
    result = st.calculate_trapezoid()

    assert 'shape' in result
    assert isinstance(result['shape'], list)
    assert len(result['shape']) > 0

    # Check that it's a valid SVG path
    svg_lines = result['shape']
    assert any('<path' in line for line in svg_lines)
    assert any('<close/>' in line for line in svg_lines)
    assert any('origin' in line for line in svg_lines)
    assert any('stackArea' in line for line in svg_lines)

  def test_custom_parameters(self):
    """Test trapezoid with custom angle and stackable percentage."""
    st = StackableTrapezoid()
    result = st.calculate_trapezoid(angle=45, notch_height=0.3, width=80, height=60)

    assert 'shape' in result
    svg_lines = result['shape']

    # Check that the path name reflects the parameters
    assert any('trapezoid_45°_0.3' in line for line in svg_lines)

    # Verify scaling was applied
    assert any('80.0' in line or '60.0' in line for line in svg_lines)

  def test_inverted_trapezoid(self):
    """Test inverted trapezoid generation."""
    st = StackableTrapezoid()
    result = st.calculate_trapezoid(invert=True)

    assert 'shape' in result
    svg_lines = result['shape']

    # Inverted trapezoid should start at bottom left (0, 0)
    assert any('<move x="0.0" y="0.0"' in line for line in svg_lines)

  def test_parameter_validation(self):
    """Test that invalid parameters raise appropriate errors."""
    st = StackableTrapezoid()

    # Test angle validation
    with pytest.raises(ValueError, match='angle should be between'):
      st.calculate_trapezoid(angle=-10)

    with pytest.raises(ValueError, match='angle should be between'):
      st.calculate_trapezoid(angle=90)

    # Test stackable_pct validation
    with pytest.raises(ValueError, match='stackable_pct should be between'):
      st.calculate_trapezoid(notch_height=0.05)

    with pytest.raises(ValueError, match='stackable_pct should be between'):
      st.calculate_trapezoid(notch_height=0.6)

  def test_extreme_angles(self):
    """Test trapezoid with extreme but valid angles."""
    st = StackableTrapezoid()

    # Very shallow angle
    result = st.calculate_trapezoid(angle=5)
    assert 'shape' in result

    # Very steep angle (should auto-adjust to prevent negative top width)
    result = st.calculate_trapezoid(angle=80)
    assert 'shape' in result

  def test_nesting_demo(self):
    """Test the nesting demonstration method."""
    st = StackableTrapezoid()
    result = st.calculate_nesting_demo(count=3)

    assert 'shapes' in result
    assert isinstance(result['shapes'], list)
    assert len(result['shapes']) == 3

    # Each shape should be a list of SVG lines
    for shape in result['shapes']:
      assert isinstance(shape, list)
      assert len(shape) > 0
      assert any('<path' in line for line in shape)

  def test_nesting_demo_validation(self):
    """Test nesting demo parameter validation."""
    st = StackableTrapezoid()

    with pytest.raises(ValueError, match='count should be between'):
      st.calculate_nesting_demo(count=1)

    with pytest.raises(ValueError, match='count should be between'):
      st.calculate_nesting_demo(count=10)

  def test_stackability(self):
    """Test that generated trapezoids have proper notch dimensions for stacking."""
    st = StackableTrapezoid()
    result = st.calculate_trapezoid(angle=70, notch_height=0.2)

    svg_lines = result['shape']

    # Check that notch-related segments are present
    assert any('stackEdge' in line for line in svg_lines)
    assert any('stackArea' in line for line in svg_lines)

    # The notch should have 3 segments (down, across, up)
    stack_area_count = sum(1 for line in svg_lines if 'stackArea' in line)
    assert stack_area_count == 3
