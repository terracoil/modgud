"""Test utilities for ShapePort refactored implementations."""

from typing import Sequence

from modgud.api.geometry import SimplexNoise, Vector
from modgud.api.geometry.svg import SVGConverter, migrate_shape_result
from modgud.domain.ports.vector_port import VectorPort


class ShapeTestUtils:
  """Utilities for testing refactored ShapePort implementations."""

  @staticmethod
  def create_test_noise(seed: int = 42, scale: float = 0.1, amplitude: float = 1.0) -> SimplexNoise:
    """Create standard test noise for consistent testing."""
    return SimplexNoise(seed=seed, scale=scale, amplitude=amplitude)

  @staticmethod
  def assert_valid_vector_sequence(vectors: Sequence[VectorPort], min_length: int = 1) -> None:
    """Assert that a sequence contains valid VectorPort objects."""
    assert isinstance(vectors, Sequence), f'Expected Sequence, got {type(vectors)}'
    assert len(vectors) >= min_length, f'Expected at least {min_length} vectors, got {len(vectors)}'

    for i, vector in enumerate(vectors):
      assert hasattr(vector, 'x'), f"Vector at index {i} missing 'x' attribute"
      assert hasattr(vector, 'y'), f"Vector at index {i} missing 'y' attribute"
      assert isinstance(vector.x, (int, float)), f'Vector.x at index {i} must be numeric'
      assert isinstance(vector.y, (int, float)), f'Vector.y at index {i} must be numeric'

  @staticmethod
  def assert_backward_compatibility(
    vectors: Sequence[VectorPort], expected_key: str = 'shape'
  ) -> dict[str, list[str]]:
    """Assert that vectors can be converted to legacy format."""
    legacy_dict = migrate_shape_result(vectors, expected_key)

    assert isinstance(legacy_dict, dict), 'Legacy result must be a dictionary'
    assert expected_key in legacy_dict, f"Dictionary must contain '{expected_key}' key"
    assert isinstance(legacy_dict[expected_key], list), 'Dictionary name must be a list'
    assert len(legacy_dict[expected_key]) > 0, 'SVG commands list must not be empty'

    # Verify SVG command structure
    svg_commands = legacy_dict[expected_key]
    assert any('<move' in cmd or '<line' in cmd for cmd in svg_commands), (
      'Must contain SVG movement commands'
    )

    return legacy_dict

  @staticmethod
  def assert_dataclass_immutability(instance, attribute_name: str, new_value) -> None:
    """Assert that dataclass instance is immutable (frozen=True)."""
    import pytest

    with pytest.raises(
      (AttributeError, Exception), match="cannot assign to field|can't set attribute"
    ):
      setattr(instance, attribute_name, new_value)

  @staticmethod
  def compare_shapes_with_same_seed(
    shape_class, params1: dict, params2: dict, seed: int = 42
  ) -> None:
    """Compare two shape instances with same seed - should produce identical results."""
    noise1 = ShapeTestUtils.create_test_noise(seed=seed)
    noise2 = ShapeTestUtils.create_test_noise(seed=seed)

    # Create instances with same noise seed
    shape1 = shape_class(noise=noise1, **params1)
    shape2 = shape_class(noise=noise2, **params2)

    result1 = shape1.build_shape()
    result2 = shape2.build_shape()

    if params1 == params2:
      # Same parameters should give identical results
      assert result1 == result2, 'Same parameters with same seed should produce identical results'
    else:
      # Different parameters should give different results
      assert result1 != result2, 'Different parameters should produce different results'

  @staticmethod
  def assert_svg_structure(
    vectors: Sequence[VectorPort], expected_min_commands: int = 2
  ) -> list[str]:
    """Assert that vectors produce valid SVG command structure."""
    svg_commands = SVGConverter.vectors_to_svg(vectors)

    assert len(svg_commands) >= expected_min_commands, (
      f'Expected at least {expected_min_commands} SVG commands'
    )

    # Should have opening and closing path tags
    assert any('<path' in cmd for cmd in svg_commands), 'Must have opening <path> tag'
    assert any('</path>' in cmd for cmd in svg_commands), 'Must have closing </path> tag'

    # Should have at least one move command
    assert any('<move' in cmd for cmd in svg_commands), 'Must have at least one <move> command'

    return svg_commands

  @staticmethod
  def create_test_vectors(count: int = 4) -> list[Vector]:
    """Create a simple sequence of test vectors."""
    return [Vector(0, 0), Vector(10, 0), Vector(10, 10), Vector(0, 10)][:count]


class ShapeParameterValidator:
  """Utilities for validating shape parameters."""

  @staticmethod
  def test_parameter_range(
    shape_class, param_name: str, valid_values: list, invalid_values: list, base_params: dict = None
  ) -> None:
    """Test parameter validation for a range of values."""
    import pytest

    base_params = base_params or {}
    noise = ShapeTestUtils.create_test_noise()

    # Test valid values
    for value in valid_values:
      params = {**base_params, param_name: value}
      shape = shape_class(noise=noise, **params)
      result = shape.build_shape()
      ShapeTestUtils.assert_valid_vector_sequence(result)

    # Test invalid values
    for value in invalid_values:
      params = {**base_params, param_name: value}
      with pytest.raises(ValueError):
        shape = shape_class(noise=noise, **params)
        # If construction succeeds, the validation might be in build_shape
        if hasattr(shape, 'build_shape'):
          shape.build_shape()

  @staticmethod
  def test_required_parameters(shape_class, required_params: list[str]) -> None:
    """Test that required parameters are enforced."""
    import pytest

    # Test missing each required parameter
    for missing_param in required_params:
      incomplete_params = {
        param: 'test_value' for param in required_params if param != missing_param
      }

      with pytest.raises((TypeError, ValueError)):
        shape_class(**incomplete_params)
