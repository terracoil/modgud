"""Comprehensive tests for Vector implementation."""

import pytest
from modgud.util import Vector, VectorProtocol


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
    """Test that Vector satisfies VectorProtocol protocol."""
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
    assert 'Vector(x=1.5, y=2.5, z=3.5, w=4.5, name=None)' == result


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


class TestProtocolSatisfaction:
  """Test that Vector satisfies VectorProtocol protocol."""

  def test_satisfies_protocol(self) -> None:
    """Test that Vector instances can be used where VectorProtocol is expected."""
    vector = Vector(1.0, 2.0, 3.0, 4.0)

    # This should not raise any type checking errors
    def use_float_vector_port(fvp: VectorProtocol) -> tuple[float, float, float, float]:
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
