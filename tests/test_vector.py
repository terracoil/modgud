"""Comprehensive tests for Vector implementation."""

import pytest
from modgud.api.geometry import Vector, VectorPort


class TestVectorConstruction:
  """Test Vector construction with various input methods."""

  def test_basic_construction(self) -> None:
    """Test basic Vector construction with x, y coordinates."""
    vector = Vector(1.0, 2.0)
    assert vector.x == 1.0
    assert vector.y == 2.0
    assert vector.z == 0.0
    assert vector.w == 0.0

  def test_full_construction(self) -> None:
    """Test Vector construction with all coordinates."""
    vector = Vector(1.5, 2.5, 3.5, 4.5)
    assert vector.x == 1.5
    assert vector.y == 2.5
    assert vector.z == 3.5
    assert vector.w == 4.5

  def test_type_coercion(self) -> None:
    """Test automatic type coercion to float."""
    vector = Vector(1, 2, 3, 4)  # integers
    assert vector.x == 1.0
    assert vector.y == 2.0
    assert vector.z == 3.0
    assert vector.w == 4.0
    assert isinstance(vector.x, float)

  def test_default_values(self) -> None:
    """Test default z and w values."""
    vector = Vector(1.0, 2.0)
    assert vector.z == 0.0
    assert vector.w == 0.0

  def test_partial_construction(self) -> None:
    """Test construction with some default values."""
    vector = Vector(1.0, 2.0, 3.0)
    assert vector.x == 1.0
    assert vector.y == 2.0
    assert vector.z == 3.0
    assert vector.w == 0.0


class TestVectorProperties:
  """Test Vector property access and protocol compliance."""

  def test_protocol_compliance(self) -> None:
    """Test that Vector satisfies VectorPort protocol."""
    vector = Vector(1.0, 2.0, 3.0, 4.0)

    # Protocol requires these properties to exist and return float
    assert hasattr(vector, 'x')
    assert hasattr(vector, 'y')
    assert hasattr(vector, 'z')
    assert hasattr(vector, 'w')

    assert isinstance(vector.x, float)
    assert isinstance(vector.y, float)
    assert isinstance(vector.z, float)
    assert isinstance(vector.w, float)

  def test_property_immutability(self) -> None:
    """Test that properties are read-only."""
    vector = Vector(1.0, 2.0, 3.0, 4.0)

    # Properties should not be settable
    with pytest.raises(AttributeError):
      vector.x = 5.0  # type: ignore


class TestAsTuple:
  """Test as_tuple method."""

  def test_as_tuple_basic(self) -> None:
    """Test basic tuple conversion."""
    vector = Vector(1.0, 2.0)
    result = vector.as_tuple()
    assert result == (1.0, 2.0, 0.0, 0.0)
    assert isinstance(result, tuple)
    assert len(result) == 4

  def test_as_tuple_full(self) -> None:
    """Test tuple conversion with all coordinates."""
    vector = Vector(1.5, 2.5, 3.5, 4.5)
    result = vector.as_tuple()
    assert result == (1.5, 2.5, 3.5, 4.5)

  def test_as_tuple_negative_values(self) -> None:
    """Test tuple conversion with negative values."""
    vector = Vector(-1.0, -2.0, -3.0, -4.0)
    result = vector.as_tuple()
    assert result == (-1.0, -2.0, -3.0, -4.0)


class TestFromDict:
  """Test Vector construction from dictionary."""

  def test_from_dict_basic(self) -> None:
    """Test basic dictionary construction."""
    vector = Vector.from_dict({'x': 1.0, 'y': 2.0})
    assert vector is not None
    assert vector.x == 1.0
    assert vector.y == 2.0
    assert vector.z == 0.0
    assert vector.w == 0.0

  def test_from_dict_full(self) -> None:
    """Test dictionary construction with all coordinates."""
    vector = Vector.from_dict({'x': 1.0, 'y': 2.0, 'z': 3.0, 'w': 4.0})
    assert vector is not None
    assert vector.x == 1.0
    assert vector.y == 2.0
    assert vector.z == 3.0
    assert vector.w == 4.0

  def test_from_dict_partial(self) -> None:
    """Test dictionary construction with z coordinate."""
    vector = Vector.from_dict({'x': 1.0, 'y': 2.0, 'z': 3.0})
    assert vector is not None
    assert vector.x == 1.0
    assert vector.y == 2.0
    assert vector.z == 3.0
    assert vector.w == 0.0

  def test_from_dict_type_coercion(self) -> None:
    """Test dictionary construction with type coercion."""
    vector = Vector.from_dict({'x': 1, 'y': 2, 'z': 3, 'w': 4})
    assert vector is not None
    assert vector.x == 1.0
    assert vector.y == 2.0
    assert vector.z == 3.0
    assert vector.w == 4.0

  def test_from_dict_missing_x(self) -> None:
    """Test dictionary construction missing x coordinate."""
    vector = Vector.from_dict({'y': 2.0})
    assert vector is None

  def test_from_dict_missing_y(self) -> None:
    """Test dictionary construction missing y coordinate."""
    vector = Vector.from_dict({'x': 1.0})
    assert vector is None

  def test_from_dict_empty(self) -> None:
    """Test dictionary construction with empty dict."""
    vector = Vector.from_dict({})
    assert vector is None

  def test_from_dict_extra_keys(self) -> None:
    """Test dictionary construction ignores extra keys."""
    vector = Vector.from_dict({'x': 1.0, 'y': 2.0, 'extra': 999})
    assert vector is not None
    assert vector.x == 1.0
    assert vector.y == 2.0


class TestFromTuple:
  """Test Vector construction from tuple."""

  def test_from_tuple_2d(self) -> None:
    """Test tuple construction with 2 elements."""
    vector = Vector.from_tuple((1.0, 2.0))
    assert vector.x == 1.0
    assert vector.y == 2.0
    assert vector.z == 0.0
    assert vector.w == 0.0

  def test_from_tuple_3d(self) -> None:
    """Test tuple construction with 3 elements."""
    vector = Vector.from_tuple((1.0, 2.0, 3.0))
    assert vector.x == 1.0
    assert vector.y == 2.0
    assert vector.z == 3.0
    assert vector.w == 0.0

  def test_from_tuple_4d(self) -> None:
    """Test tuple construction with 4 elements."""
    vector = Vector.from_tuple((1.0, 2.0, 3.0, 4.0))
    assert vector.x == 1.0
    assert vector.y == 2.0
    assert vector.z == 3.0
    assert vector.w == 4.0

  def test_from_tuple_extra_elements(self) -> None:
    """Test tuple construction ignores extra elements."""
    vector = Vector.from_tuple((1.0, 2.0, 3.0, 4.0, 5.0, 6.0))
    assert vector.x == 1.0
    assert vector.y == 2.0
    assert vector.z == 3.0
    assert vector.w == 4.0

  def test_from_tuple_vector_input(self) -> None:
    """Test tuple construction with Vector input."""
    original = Vector(1.0, 2.0, 3.0, 4.0)
    vector = Vector.from_tuple(original)  # type: ignore
    assert vector is original  # Should return same instance

  def test_from_tuple_list_input(self) -> None:
    """Test tuple construction with list input."""
    vector = Vector.from_tuple([1.0, 2.0, 3.0, 4.0])  # type: ignore
    assert vector.x == 1.0
    assert vector.y == 2.0
    assert vector.z == 3.0
    assert vector.w == 4.0

  def test_from_tuple_too_short(self) -> None:
    """Test tuple construction with insufficient elements."""
    with pytest.raises(ValueError, match='must have at least 2 elements'):
      Vector.from_tuple((1.0,))

  def test_from_tuple_empty(self) -> None:
    """Test tuple construction with empty tuple."""
    with pytest.raises(ValueError, match='must have at least 2 elements'):
      Vector.from_tuple(())

  def test_from_tuple_invalid_type(self) -> None:
    """Test tuple construction with invalid type."""
    with pytest.raises(ValueError, match='could not convert string to float'):
      Vector.from_tuple('not_iterable')  # type: ignore


class TestFromInput:
  """Test Vector construction from various input types."""

  def test_from_input_dict(self) -> None:
    """Test from_input with dictionary."""
    vectors = Vector.from_input({'x': 1.0, 'y': 2.0})
    assert len(vectors) == 1
    assert vectors[0].x == 1.0
    assert vectors[0].y == 2.0

  def test_from_input_dict_invalid(self) -> None:
    """Test from_input with invalid dictionary."""
    vectors = Vector.from_input({'y': 2.0})  # missing x
    assert len(vectors) == 0

  def test_from_input_vector(self) -> None:
    """Test from_input with Vector instance."""
    original = Vector(1.0, 2.0)
    vectors = Vector.from_input(original)
    assert len(vectors) == 1
    assert vectors[0] is original

  def test_from_input_tuple(self) -> None:
    """Test from_input with tuple."""
    vectors = Vector.from_input((1.0, 2.0, 3.0))
    assert len(vectors) == 1
    assert vectors[0].x == 1.0
    assert vectors[0].y == 2.0
    assert vectors[0].z == 3.0

  def test_from_input_list_of_dicts(self) -> None:
    """Test from_input with list of dictionaries."""
    input_data = [{'x': 1.0, 'y': 2.0}, {'x': 3.0, 'y': 4.0, 'z': 5.0}]
    vectors = Vector.from_input(input_data)
    assert len(vectors) == 2
    assert vectors[0].x == 1.0
    assert vectors[0].y == 2.0
    assert vectors[1].x == 3.0
    assert vectors[1].y == 4.0
    assert vectors[1].z == 5.0

  def test_from_input_list_of_tuples(self) -> None:
    """Test from_input with list of tuples."""
    input_data = [(1.0, 2.0), (3.0, 4.0, 5.0)]
    vectors = Vector.from_input(input_data)
    assert len(vectors) == 2
    assert vectors[0].x == 1.0
    assert vectors[0].y == 2.0
    assert vectors[1].x == 3.0
    assert vectors[1].y == 4.0
    assert vectors[1].z == 5.0

  def test_from_input_list_mixed(self) -> None:
    """Test from_input with mixed list."""
    original_vector = Vector(1.0, 2.0)
    input_data = [original_vector, {'x': 3.0, 'y': 4.0}, (5.0, 6.0, 7.0)]
    vectors = Vector.from_input(input_data)
    assert len(vectors) == 3
    assert vectors[0] is original_vector
    assert vectors[1].x == 3.0
    assert vectors[2].x == 5.0

  def test_from_input_unsupported_type(self) -> None:
    """Test from_input with unsupported type."""
    with pytest.raises(ValueError, match='Unsupported type'):
      Vector.from_input('invalid_string')  # type: ignore

  def test_from_input_empty_list(self) -> None:
    """Test from_input with empty list."""
    vectors = Vector.from_input([])
    assert len(vectors) == 0


class TestFromArgs:
  """Test legacy from_args method."""

  def test_from_args_delegates_to_from_dict(self) -> None:
    """Test that from_args delegates to from_dict."""
    vector = Vector.from_args({'x': 1.0, 'y': 2.0})
    assert vector is not None
    assert vector.x == 1.0
    assert vector.y == 2.0


class TestVectorEquality:
  """Test Vector equality comparison."""

  def test_equality_same_values(self) -> None:
    """Test equality with same values."""
    v1 = Vector(1.0, 2.0, 3.0, 4.0)
    v2 = Vector(1.0, 2.0, 3.0, 4.0)
    assert v1 == v2

  def test_equality_different_values(self) -> None:
    """Test inequality with different values."""
    v1 = Vector(1.0, 2.0, 3.0, 4.0)
    v2 = Vector(1.0, 2.0, 3.0, 5.0)
    assert v1 != v2

  def test_equality_with_non_vector(self) -> None:
    """Test equality with non-Vector object."""
    v1 = Vector(1.0, 2.0)
    assert v1 != 'not_a_vector'
    assert v1 != (1.0, 2.0)
    assert v1 != {'x': 1.0, 'y': 2.0}

  def test_equality_default_values(self) -> None:
    """Test equality considers default values."""
    v1 = Vector(1.0, 2.0)
    v2 = Vector(1.0, 2.0, 0.0, 0.0)
    assert v1 == v2


class TestVectorRepresentation:
  """Test Vector string representation."""

  def test_repr_basic(self) -> None:
    """Test basic string representation."""
    vector = Vector(1.0, 2.0)
    result = repr(vector)
    assert 'Vector(' in result
    assert 'x=1.0' in result
    assert 'y=2.0' in result
    assert 'z=0.0' in result
    assert 'w=0.0' in result

  def test_repr_full(self) -> None:
    """Test string representation with all coordinates."""
    vector = Vector(1.5, 2.5, 3.5, 4.5)
    result = repr(vector)
    assert "Vector(x=1.5, y=2.5, z=3.5, w=4.5, name='')" == result


class TestEdgeCases:
  """Test edge cases and error conditions."""

  def test_negative_coordinates(self) -> None:
    """Test Vector with negative coordinates."""
    vector = Vector(-1.0, -2.0, -3.0, -4.0)
    assert vector.x == -1.0
    assert vector.y == -2.0
    assert vector.z == -3.0
    assert vector.w == -4.0

  def test_zero_coordinates(self) -> None:
    """Test Vector with zero coordinates."""
    vector = Vector(0.0, 0.0, 0.0, 0.0)
    assert vector.x == 0.0
    assert vector.y == 0.0
    assert vector.z == 0.0
    assert vector.w == 0.0

  def test_large_coordinates(self) -> None:
    """Test Vector with large coordinates."""
    large_val = 1e10
    vector = Vector(large_val, large_val, large_val, large_val)
    assert vector.x == large_val
    assert vector.y == large_val
    assert vector.z == large_val
    assert vector.w == large_val

  def test_small_coordinates(self) -> None:
    """Test Vector with very small coordinates."""
    small_val = 1e-10
    vector = Vector(small_val, small_val, small_val, small_val)
    assert vector.x == small_val
    assert vector.y == small_val
    assert vector.z == small_val
    assert vector.w == small_val

  def test_hex_word_coordinates(self) -> None:
    """Test Vector with hex word test data (project convention)."""
    # Using "words" made from hex digits: dead, beef, cafe, babe
    vector = Vector(0xDEAD, 0xBEEF, 0xCAFE, 0xBABE)
    assert vector.x == 0xDEAD
    assert vector.y == 0xBEEF
    assert vector.z == 0xCAFE
    assert vector.w == 0xBABE


class TestArithmeticOperations:
  """Test vector arithmetic operations."""

  def test_addition(self) -> None:
    """Test vector addition."""
    v1 = Vector(1.0, 2.0, 3.0, 4.0, name='v1')
    v2 = Vector(5.0, 6.0, 7.0, 8.0, name='v2')
    result = v1 + v2

    assert result.x == 6.0
    assert result.y == 8.0
    assert result.z == 10.0
    assert result.w == 12.0
    assert result.name == 'v2'  # Preserves other vector's name

  def test_subtraction(self) -> None:
    """Test vector subtraction."""
    v1 = Vector(10.0, 8.0, 6.0, 4.0, name='v1')
    v2 = Vector(5.0, 3.0, 2.0, 1.0, name='v2')
    result = v1 - v2

    assert result.x == 5.0
    assert result.y == 5.0
    assert result.z == 4.0
    assert result.w == 3.0
    assert result.name == 'v2'  # Preserves other vector's name

  def test_multiplication(self) -> None:
    """Test component-wise multiplication."""
    v1 = Vector(2.0, 3.0, 4.0, 5.0, name='v1')
    v2 = Vector(10.0, 20.0, 30.0, 40.0, name='v2')
    result = v1 * v2

    assert result.x == 20.0
    assert result.y == 60.0
    assert result.z == 120.0
    assert result.w == 200.0
    assert result.name == 'v2'  # Preserves other vector's name

  def test_division(self) -> None:
    """Test component-wise division."""
    v1 = Vector(100.0, 50.0, 25.0, 10.0, name='v1')
    v2 = Vector(10.0, 5.0, 5.0, 2.0, name='v2')
    result = v1 / v2

    assert result.x == 10.0
    assert result.y == 10.0
    assert result.z == 5.0
    assert result.w == 5.0
    assert result.name == 'v2'  # Preserves other vector's name

  def test_division_by_zero(self) -> None:
    """Test division by zero raises exception."""
    v1 = Vector(1.0, 2.0, 3.0, 4.0)
    v2 = Vector(0.0, 1.0, 0.0, 1.0)

    with pytest.raises(ZeroDivisionError):
      _ = v1 / v2


class TestVectorClone:
  """Test Vector clone method."""

  def test_clone_no_changes(self) -> None:
    """Test clone with no parameters creates identical copy."""
    original = Vector(1.0, 2.0, 3.0, 4.0, name='original')
    cloned = original.clone()

    assert cloned == original
    assert cloned is not original  # Different instance
    assert cloned.x == 1.0
    assert cloned.y == 2.0
    assert cloned.z == 3.0
    assert cloned.w == 4.0
    assert cloned.name == 'original'

  def test_clone_change_x(self) -> None:
    """Test clone with x override."""
    original = Vector(1.0, 2.0, 3.0, 4.0, name='original')
    cloned = original.clone(x=10.0)

    assert cloned.x == 10.0
    assert cloned.y == 2.0
    assert cloned.z == 3.0
    assert cloned.w == 4.0
    assert cloned.name == 'original'

  def test_clone_change_y(self) -> None:
    """Test clone with y override."""
    original = Vector(1.0, 2.0, 3.0, 4.0, name='original')
    cloned = original.clone(y=20.0)

    assert cloned.x == 1.0
    assert cloned.y == 20.0
    assert cloned.z == 3.0
    assert cloned.w == 4.0
    assert cloned.name == 'original'

  def test_clone_change_z(self) -> None:
    """Test clone with z override."""
    original = Vector(1.0, 2.0, 3.0, 4.0, name='original')
    cloned = original.clone(z=30.0)

    assert cloned.x == 1.0
    assert cloned.y == 2.0
    assert cloned.z == 30.0
    assert cloned.w == 4.0
    assert cloned.name == 'original'

  def test_clone_change_w(self) -> None:
    """Test clone with w override."""
    original = Vector(1.0, 2.0, 3.0, 4.0, name='original')
    cloned = original.clone(w=40.0)

    assert cloned.x == 1.0
    assert cloned.y == 2.0
    assert cloned.z == 3.0
    assert cloned.w == 40.0
    assert cloned.name == 'original'

  def test_clone_change_name(self) -> None:
    """Test clone with name override."""
    original = Vector(1.0, 2.0, 3.0, 4.0, name='original')
    cloned = original.clone(name='cloned')

    assert cloned.x == 1.0
    assert cloned.y == 2.0
    assert cloned.z == 3.0
    assert cloned.w == 4.0
    assert cloned.name == 'cloned'

  def test_clone_multiple_changes(self) -> None:
    """Test clone with multiple component overrides."""
    original = Vector(1.0, 2.0, 3.0, 4.0, name='original')
    cloned = original.clone(x=10.0, z=30.0, name='modified')

    assert cloned.x == 10.0
    assert cloned.y == 2.0  # unchanged
    assert cloned.z == 30.0
    assert cloned.w == 4.0  # unchanged
    assert cloned.name == 'modified'

  def test_clone_all_changes(self) -> None:
    """Test clone with all components overridden."""
    original = Vector(1.0, 2.0, 3.0, 4.0, name='original')
    cloned = original.clone(x=10.0, y=20.0, z=30.0, w=40.0, name='new')

    assert cloned.x == 10.0
    assert cloned.y == 20.0
    assert cloned.z == 30.0
    assert cloned.w == 40.0
    assert cloned.name == 'new'

  def test_clone_with_zero_values(self) -> None:
    """Test clone with zero value overrides."""
    original = Vector(1.0, 2.0, 3.0, 4.0, name='original')
    cloned = original.clone(x=0.0, y=0.0)

    assert cloned.x == 0.0
    assert cloned.y == 0.0
    assert cloned.z == 3.0
    assert cloned.w == 4.0
    assert cloned.name == 'original'

  def test_clone_with_negative_values(self) -> None:
    """Test clone with negative value overrides."""
    original = Vector(1.0, 2.0, 3.0, 4.0, name='original')
    cloned = original.clone(x=-10.0, w=-40.0)

    assert cloned.x == -10.0
    assert cloned.y == 2.0
    assert cloned.z == 3.0
    assert cloned.w == -40.0
    assert cloned.name == 'original'

  def test_clone_empty_name_to_named(self) -> None:
    """Test clone from vector with empty name to named vector."""
    original = Vector(1.0, 2.0, 3.0, 4.0)  # name=''
    cloned = original.clone(name='named')

    assert cloned.x == 1.0
    assert cloned.y == 2.0
    assert cloned.z == 3.0
    assert cloned.w == 4.0
    assert cloned.name == 'named'
    assert original.name == ''

  def test_clone_named_to_empty_name(self) -> None:
    """Test clone from named vector to empty name - name parameter should be explicitly set."""
    original = Vector(1.0, 2.0, 3.0, 4.0, name='original')
    # Note: passing name='' explicitly should set name to empty string
    cloned = original.clone(name='')

    assert cloned.x == 1.0
    assert cloned.y == 2.0
    assert cloned.z == 3.0
    assert cloned.w == 4.0
    assert cloned.name == ''
    assert original.name == 'original'

  def test_clone_type_coercion(self) -> None:
    """Test clone with integer inputs that get coerced to float."""
    original = Vector(1.5, 2.5, 3.5, 4.5, name='original')
    cloned = original.clone(x=10, y=20)  # integers

    assert cloned.x == 10.0
    assert cloned.y == 20.0
    assert isinstance(cloned.x, float)
    assert isinstance(cloned.y, float)
    assert cloned.z == 3.5
    assert cloned.w == 4.5

  def test_clone_returns_vector_protocol(self) -> None:
    """Test clone returns object satisfying VectorPort."""
    original = Vector(1.0, 2.0, 3.0, 4.0)
    cloned = original.clone(x=10.0)

    # Should satisfy protocol
    assert isinstance(cloned, VectorPort)
    assert hasattr(cloned, 'x')
    assert hasattr(cloned, 'y')
    assert hasattr(cloned, 'z')
    assert hasattr(cloned, 'w')
    assert hasattr(cloned, 'name')


class TestVectorInverse:
  """Test Vector inverse method."""

  def test_inverse_basic(self) -> None:
    """Test inverse with positive components."""
    original = Vector(1.0, 2.0, 3.0, 4.0, name='original')
    inverted = original.inverse()

    assert inverted.x == -1.0
    assert inverted.y == -2.0
    assert inverted.z == -3.0
    assert inverted.w == -4.0
    assert inverted.name == 'original'  # Name preserved

  def test_inverse_negative_components(self) -> None:
    """Test inverse with negative components."""
    original = Vector(-1.0, -2.0, -3.0, -4.0, name='negative')
    inverted = original.inverse()

    assert inverted.x == 1.0
    assert inverted.y == 2.0
    assert inverted.z == 3.0
    assert inverted.w == 4.0
    assert inverted.name == 'negative'

  def test_inverse_mixed_components(self) -> None:
    """Test inverse with mixed positive/negative components."""
    original = Vector(-1.0, 2.0, -3.0, 4.0, name='mixed')
    inverted = original.inverse()

    assert inverted.x == 1.0
    assert inverted.y == -2.0
    assert inverted.z == 3.0
    assert inverted.w == -4.0
    assert inverted.name == 'mixed'

  def test_inverse_zero_components(self) -> None:
    """Test inverse with zero components."""
    original = Vector(0.0, 0.0, 0.0, 0.0, name='zero')
    inverted = original.inverse()

    assert inverted.x == 0.0
    assert inverted.y == 0.0
    assert inverted.z == 0.0
    assert inverted.w == 0.0
    assert inverted.name == 'zero'

  def test_inverse_2d_vector(self) -> None:
    """Test inverse with 2D vector (z=0, w=0)."""
    original = Vector(5.0, -3.0)  # z=0, w=0 by default
    inverted = original.inverse()

    assert inverted.x == -5.0
    assert inverted.y == 3.0
    assert inverted.z == 0.0
    assert inverted.w == 0.0

  def test_inverse_preserves_name(self) -> None:
    """Test that inverse preserves the original name."""
    original = Vector(1.0, 2.0, name='test_name')
    inverted = original.inverse()

    assert inverted.name == 'test_name'
    assert original.name == 'test_name'  # Original unchanged

  def test_inverse_empty_name(self) -> None:
    """Test inverse with empty name."""
    original = Vector(1.0, 2.0)  # name='' by default
    inverted = original.inverse()

    assert inverted.name == ''
    assert inverted.x == -1.0
    assert inverted.y == -2.0

  def test_inverse_additive_identity_property(self) -> None:
    """Test that v + v.inverse() = ZERO (additive identity property)."""
    original = Vector(3.0, 4.0, 5.0, 6.0, name='test')
    inverted = original.inverse()
    result = original + inverted

    # Should equal ZERO vector (allowing for floating point precision)
    assert abs(result.x) < 1e-10
    assert abs(result.y) < 1e-10
    assert abs(result.z) < 1e-10
    assert abs(result.w) < 1e-10

  def test_inverse_double_negation(self) -> None:
    """Test that inverse of inverse returns original (double negation)."""
    original = Vector(2.0, -3.0, 4.0, -5.0, name='original')
    double_inverse = original.inverse().inverse()

    assert double_inverse.x == original.x
    assert double_inverse.y == original.y
    assert double_inverse.z == original.z
    assert double_inverse.w == original.w
    assert double_inverse.name == original.name

  def test_inverse_returns_new_instance(self) -> None:
    """Test that inverse creates a new instance, not modifying the original."""
    original = Vector(1.0, 2.0, 3.0, 4.0, name='original')
    inverted = original.inverse()

    # Should be different instances
    assert inverted is not original

    # Original should be unchanged
    assert original.x == 1.0
    assert original.y == 2.0
    assert original.z == 3.0
    assert original.w == 4.0
    assert original.name == 'original'

  def test_inverse_with_zero_vector(self) -> None:
    """Test inverse of ZERO vector."""
    zero = Vector.ZERO
    inverted = zero.inverse()

    assert inverted == Vector.ZERO
    assert inverted.x == 0.0
    assert inverted.y == 0.0
    assert inverted.z == 0.0
    assert inverted.w == 0.0

  def test_inverse_returns_vector_protocol(self) -> None:
    """Test inverse returns object satisfying VectorPort."""
    original = Vector(1.0, 2.0)
    inverted = original.inverse()

    # Should satisfy protocol
    assert isinstance(inverted, VectorPort)
    assert hasattr(inverted, 'x')
    assert hasattr(inverted, 'y')
    assert hasattr(inverted, 'z')
    assert hasattr(inverted, 'w')
    assert hasattr(inverted, 'name')

  def test_inverse_with_large_values(self) -> None:
    """Test inverse with large floating point values."""
    large_val = 1e10
    original = Vector(large_val, -large_val, large_val, -large_val)
    inverted = original.inverse()

    assert inverted.x == -large_val
    assert inverted.y == large_val
    assert inverted.z == -large_val
    assert inverted.w == large_val

  def test_inverse_with_small_values(self) -> None:
    """Test inverse with very small floating point values."""
    small_val = 1e-10
    original = Vector(small_val, -small_val, small_val, -small_val)
    inverted = original.inverse()

    assert inverted.x == -small_val
    assert inverted.y == small_val
    assert inverted.z == -small_val
    assert inverted.w == small_val


class TestProtocolSatisfaction:
  """Test that Vector satisfies VectorPort protocol."""

  def test_satisfies_protocol(self) -> None:
    """Test that Vector instances can be used where VectorPort is expected."""
    vector = Vector(1.0, 2.0, 3.0, 4.0)

    # This should not raise any type checking errors
    def use_float_vector_port(fvp: VectorPort) -> tuple[float, float, float, float]:
      return (fvp.x, fvp.y, fvp.z, fvp.w)

    result = use_float_vector_port(vector)
    assert result == (1.0, 2.0, 3.0, 4.0)

  def test_protocol_properties_return_float(self) -> None:
    """Test that all protocol properties return float type."""
    vector = Vector(1, 2, 3, 4)  # Pass integers

    assert isinstance(vector.x, float)
    assert isinstance(vector.y, float)
    assert isinstance(vector.z, float)
    assert isinstance(vector.w, float)


class TestVectorPathSubscriptable:
  """Test VectorPath subscriptable functionality."""

  def test_getitem_origin(self) -> None:
    """Test accessing origin via index 0."""
    from modgud.api.geometry import VectorPath

    origin = Vector(1.0, 2.0)
    path = VectorPath(rel_segments=origin)

    result = path[0]
    assert result == origin
    assert result.x == 1.0
    assert result.y == 2.0

  def test_getitem_rel_segments(self) -> None:
    """Test accessing relative segments via index > 0."""
    from modgud.api.geometry import VectorPath

    origin = Vector(0.0, 0.0)
    seg1 = Vector(1.0, 0.0)
    seg2 = Vector(0.0, 1.0)
    seg3 = Vector(-1.0, 0.0)

    path = VectorPath(rel_segments=origin)
    path.push_segment([seg1, seg2, seg3])

    # Test accessing each segment
    assert path[0] == origin
    assert path[1] == seg1
    assert path[2] == seg2
    assert path[3] == seg3

  def test_getitem_index_out_of_bounds_negative(self) -> None:
    """Test accessing with negative index raises IndexError."""
    from modgud.api.geometry import VectorPath

    path = VectorPath(rel_segments=Vector(0.0, 0.0))
    path.push_segment(Vector(1.0, 1.0))

    with pytest.raises(IndexError, match='Path index -1 out of range'):
      _ = path[-1]

  def test_getitem_index_out_of_bounds_too_high(self) -> None:
    """Test accessing with index >= length raises IndexError."""
    from modgud.api.geometry import VectorPath

    path = VectorPath(rel_segments=Vector(0.0, 0.0))
    path.push_segment(Vector(1.0, 1.0))

    # Path has length 2 (origin + 1 segment), so index 2 should be out of bounds
    with pytest.raises(IndexError, match='Path index 2 out of range'):
      _ = path[2]

  def test_getitem_empty_path(self) -> None:
    """Test accessing path with only origin."""
    from modgud.api.geometry import VectorPath

    origin = Vector(5.0, 10.0)
    path = VectorPath(rel_segments=origin)

    # Should be able to access origin
    assert path[0] == origin

    # Index 1 should be out of bounds
    with pytest.raises(IndexError, match='Path index 1 out of range'):
      _ = path[1]

  def test_getitem_consistency_with_len(self) -> None:
    """Test that subscriptable access is consistent with __len__."""
    from modgud.api.geometry import VectorPath

    origin = Vector(0.0, 0.0)
    segments = [Vector(1.0, 0.0), Vector(0.0, 1.0), Vector(-1.0, 0.0)]

    path = VectorPath(rel_segments=origin)
    path.push_segment(segments)

    path_length = len(path)
    assert path_length == 4  # origin + 3 segments

    # Should be able to access indices 0 through length-1
    for i in range(path_length):
      _ = path[i]  # Should not raise

    # Index equal to length should raise
    with pytest.raises(IndexError):
      _ = path[path_length]

  def test_getitem_with_named_vectors(self) -> None:
    """Test accessing path with named vectors preserves names."""
    from modgud.api.geometry import VectorPath

    origin = Vector(0.0, 0.0, name='start')
    seg1 = Vector(1.0, 0.0, name='right')
    seg2 = Vector(0.0, 1.0, name='up')

    path = VectorPath(rel_segments=origin)
    path.push_segment([seg1, seg2])

    assert path[0].name == 'start'
    assert path[1].name == 'right'
    assert path[2].name == 'up'
