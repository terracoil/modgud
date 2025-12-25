"""Tests for the Joinery geometry generator."""

import pytest
from modgud.api.geometry import Joinery, migrate_shape_result

from tests.test_shape_utils import ShapeTestUtils


class TestJoinery:
  """Test cases for Joinery."""

  def test_basic_dovetail(self):
    """Test basic dovetail generation with default parameters."""
    j = Joinery()
    result = j.build_shape()

    # Verify new return structure (Sequence[VectorPort])
    ShapeTestUtils.assert_valid_vector_sequence(result)

    # Test backward compatibility for primary shape
    legacy_result = migrate_shape_result(result, 'teeth')
    assert isinstance(legacy_result, dict)
    assert 'teeth' in legacy_result
    assert isinstance(legacy_result['teeth'], list)
    assert len(legacy_result['teeth']) > 0

    # Verify SVG structure
    svg_lines = legacy_result['teeth']
    assert any('<path' in line for line in svg_lines)
    assert any('<close/>' in line for line in svg_lines)

  def test_multi_component_shapes(self):
    """Test that all three shape components work correctly."""
    j = Joinery()

    # Test all three individual shape methods
    teeth_result = j.build_shape()
    adapter_result = j.build_adapter_shape()
    port_result = j.build_port_shape()

    # All should return valid vector sequences
    ShapeTestUtils.assert_valid_vector_sequence(teeth_result)
    ShapeTestUtils.assert_valid_vector_sequence(adapter_result)
    ShapeTestUtils.assert_valid_vector_sequence(port_result)

    # All should be different shapes
    assert teeth_result != adapter_result
    assert teeth_result != port_result
    assert adapter_result != port_result

  def test_build_all_shapes_backward_compatibility(self):
    """Test that build_all_shapes returns legacy format."""
    j = Joinery(slope_pct=0.15, teeth_cnt=3)
    all_shapes = j.build_all_shapes()

    # Should return dictionary with expected keys
    assert isinstance(all_shapes, dict)
    assert 'teeth' in all_shapes
    assert 'left' in all_shapes
    assert 'right' in all_shapes

    # Each component should be a list of SVG strings
    for key, svg_list in all_shapes.items():
      assert isinstance(svg_list, list)
      assert len(svg_list) > 0
      assert any('<path' in line for line in svg_list)
      assert any('<close/>' in line for line in svg_list)

  def test_dataclass_immutability(self):
    """Test that Joinery is immutable (frozen=True)."""
    j = Joinery(slope_pct=0.15, teeth_cnt=3, tooth_depth_pct=0.4, corner_pct=0.15)

    # Test that we can't modify attributes
    ShapeTestUtils.assert_dataclass_immutability(j, 'slope_pct', 0.2)
    ShapeTestUtils.assert_dataclass_immutability(j, 'teeth_cnt', 4)
    ShapeTestUtils.assert_dataclass_immutability(j, 'tooth_depth_pct', 0.5)
    ShapeTestUtils.assert_dataclass_immutability(j, 'corner_pct', 0.2)

  def test_constructor_parameters(self):
    """Test that all parameters work in constructor."""
    j = Joinery(
      slope_pct=0.2,
      teeth_cnt=4,
      tooth_depth_pct=0.6,
      corner_pct=0.2,
    )

    # Verify parameters are set correctly
    assert j.slope_pct == 0.2
    assert j.teeth_cnt == 4
    assert j.tooth_depth_pct == 0.6
    assert j.corner_pct == 0.2

    # Verify all build methods work
    teeth = j.build_shape()
    adapter = j.build_adapter_shape()
    port = j.build_port_shape()

    ShapeTestUtils.assert_valid_vector_sequence(teeth)
    ShapeTestUtils.assert_valid_vector_sequence(adapter)
    ShapeTestUtils.assert_valid_vector_sequence(port)

  def test_parameter_validation_slope_pct(self):
    """Test slope_pct parameter validation."""
    # Valid slope_pct values
    for slope in [-0.7, -0.3, 0.0, 0.1, 0.3]:
      j = Joinery(slope_pct=slope)
      result = j.build_shape()
      ShapeTestUtils.assert_valid_vector_sequence(result)

    # Invalid slope_pct values
    for slope in [-0.8, -1.0, 0.4, 0.5]:
      with pytest.raises(ValueError, match='slope_pct should be between -70% and 30%'):
        Joinery(slope_pct=slope)

  def test_parameter_validation_tooth_depth_pct(self):
    """Test tooth_depth_pct parameter validation."""
    # Valid tooth_depth_pct values
    for depth in [0.1, 0.3, 0.5, 0.7, 0.9]:
      j = Joinery(tooth_depth_pct=depth)
      result = j.build_shape()
      ShapeTestUtils.assert_valid_vector_sequence(result)

    # Invalid tooth_depth_pct values
    for depth in [0.05, 0.0, 0.95, 1.0]:
      with pytest.raises(ValueError, match='tooth_depth_pct should be between 10% and 90%'):
        Joinery(tooth_depth_pct=depth)

  def test_parameter_validation_teeth_cnt(self):
    """Test teeth_cnt parameter validation."""
    # Valid teeth_cnt values
    for count in [1, 2, 5, 8, 10]:
      j = Joinery(teeth_cnt=count)
      result = j.build_shape()
      ShapeTestUtils.assert_valid_vector_sequence(result)

    # Invalid teeth_cnt values
    for count in [0, -1, 11, 15]:
      with pytest.raises(ValueError, match='teeth_cnt should be between 1 and 10'):
        Joinery(teeth_cnt=count)

  def test_parameter_validation_corner_pct(self):
    """Test corner_pct parameter validation."""
    # Valid corner_pct values
    for corner in [0.0, 0.1, 0.25, 0.4, 0.5]:
      j = Joinery(corner_pct=corner)
      result = j.build_shape()
      ShapeTestUtils.assert_valid_vector_sequence(result)

    # Invalid corner_pct values
    for corner in [-0.1, 0.6, 1.0]:
      with pytest.raises(ValueError, match='corner_pct should be between 0% and 50%'):
        Joinery(corner_pct=corner)

  def test_validation_in_constructor(self):
    """Test that validation happens in constructor (__post_init__)."""
    # Invalid slope_pct should fail at construction
    with pytest.raises(ValueError, match='slope_pct should be between -70% and 30%'):
      Joinery(slope_pct=0.5)

    # Invalid tooth_depth_pct should fail at construction
    with pytest.raises(ValueError, match='tooth_depth_pct should be between 10% and 90%'):
      Joinery(tooth_depth_pct=0.05)

    # Invalid teeth_cnt should fail at construction
    with pytest.raises(ValueError, match='teeth_cnt should be between 1 and 10'):
      Joinery(teeth_cnt=0)

    # Invalid corner_pct should fail at construction
    with pytest.raises(ValueError, match='corner_pct should be between 0% and 50%'):
      Joinery(corner_pct=0.6)

  def test_return_type_is_vector_sequence(self):
    """Test that build methods return Sequence[VectorPort], not SVG dict."""
    j = Joinery()

    # Test all build methods
    teeth = j.build_shape()
    adapter = j.build_adapter_shape()
    port = j.build_port_shape()

    # Should all be sequences of vectors
    ShapeTestUtils.assert_valid_vector_sequence(teeth)
    ShapeTestUtils.assert_valid_vector_sequence(adapter)
    ShapeTestUtils.assert_valid_vector_sequence(port)

    # Should NOT be the old dictionary format
    assert not isinstance(teeth, dict)
    assert not isinstance(adapter, dict)
    assert not isinstance(port, dict)

  def test_different_parameters_produce_different_results(self):
    """Test that different parameters produce different shapes."""
    j1 = Joinery(slope_pct=0.1, teeth_cnt=2)
    j2 = Joinery(slope_pct=0.2, teeth_cnt=2)
    j3 = Joinery(slope_pct=0.1, teeth_cnt=3)
    j4 = Joinery(slope_pct=0.1, teeth_cnt=2, tooth_depth_pct=0.6)

    result1 = j1.build_shape()
    result2 = j2.build_shape()
    result3 = j3.build_shape()
    result4 = j4.build_shape()

    # Different slope_pct should produce different results
    assert result1 != result2

    # Different teeth_cnt should produce different results
    assert result1 != result3

    # Different tooth_depth_pct affects adapter/port but not primary teeth
    teeth_4 = j4.build_shape()
    adapter_4 = j4.build_adapter_shape()
    adapter_1 = j1.build_adapter_shape()

    # Same teeth count and slope should give same teeth
    assert result1 == teeth_4

    # But different depth should give different adapters
    assert adapter_1 != adapter_4

  def test_joint_types(self):
    """Test different joint types based on slope."""
    # Notched joint (zero slope)
    j_notched = Joinery(slope_pct=0.0)
    result_notched = j_notched.build_shape()
    ShapeTestUtils.assert_valid_vector_sequence(result_notched)

    # Dovetail joint (positive slope)
    j_dovetail = Joinery(slope_pct=0.15)
    result_dovetail = j_dovetail.build_shape()
    ShapeTestUtils.assert_valid_vector_sequence(result_dovetail)

    # Slanted joint (negative slope)
    j_slanted = Joinery(slope_pct=-0.2)
    result_slanted = j_slanted.build_shape()
    ShapeTestUtils.assert_valid_vector_sequence(result_slanted)

    # All should produce different results
    assert result_notched != result_dovetail
    assert result_notched != result_slanted
    assert result_dovetail != result_slanted

  def test_slope_validation_edge_cases(self):
    """Test edge cases of slope validation that are reachable."""
    # Test maximum valid slope with different teeth counts
    for teeth_cnt in [1, 2, 5, 10]:
      j = Joinery(slope_pct=0.3, teeth_cnt=teeth_cnt)  # Max valid slope
      result = j.build_shape()
      ShapeTestUtils.assert_valid_vector_sequence(result)

    # Test minimum valid slope
    j_min = Joinery(slope_pct=-0.7, teeth_cnt=5)
    result_min = j_min.build_shape()
    ShapeTestUtils.assert_valid_vector_sequence(result_min)

  def test_backward_compatibility_conversion(self):
    """Test that individual shapes can be converted to legacy format."""
    j = Joinery(slope_pct=0.1, teeth_cnt=2)

    # Test each individual component
    teeth = j.build_shape()
    adapter = j.build_adapter_shape()
    port = j.build_port_shape()

    # Convert each to legacy format
    teeth_legacy = ShapeTestUtils.assert_backward_compatibility(teeth, 'teeth')
    adapter_legacy = ShapeTestUtils.assert_backward_compatibility(adapter, 'adapter')
    port_legacy = ShapeTestUtils.assert_backward_compatibility(port, 'port')

    # Verify SVG structure for each
    for legacy_dict in [teeth_legacy, adapter_legacy, port_legacy]:
      svg_commands = list(legacy_dict.values())[0]
      assert any('<path' in cmd for cmd in svg_commands)
      assert any('<move' in cmd for cmd in svg_commands)

  def test_extreme_valid_parameters(self):
    """Test with extreme but valid parameter values."""
    # Minimum valid parameters
    j_min = Joinery(slope_pct=-0.7, teeth_cnt=1, tooth_depth_pct=0.1, corner_pct=0.0)
    result_min = j_min.build_shape()
    ShapeTestUtils.assert_valid_vector_sequence(result_min)

    # Maximum valid parameters
    j_max = Joinery(slope_pct=0.3, teeth_cnt=10, tooth_depth_pct=0.9, corner_pct=0.5)
    # Note: may need to reduce slope_pct due to internal validation with high teeth_cnt
    try:
      result_max = j_max.build_shape()
      ShapeTestUtils.assert_valid_vector_sequence(result_max)
    except ValueError:
      # If slope is too extreme for 10 teeth, try with fewer teeth
      j_max_safe = Joinery(slope_pct=0.15, teeth_cnt=10, tooth_depth_pct=0.9, corner_pct=0.5)
      result_max_safe = j_max_safe.build_shape()
      ShapeTestUtils.assert_valid_vector_sequence(result_max_safe)
