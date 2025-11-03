"""Tests for the @pipeable decorator core functionality."""

import pytest

from modgud import pipeable
from modgud.guarded_expression.pipeable import Pipeable


# Test functions to use in pipelines
@pipeable
def add(x, y):
  """Add two numbers."""
  return x + y


@pipeable
def multiply(x, factor):
  """Multiply by a factor."""
  return x * factor


@pipeable
def subtract(x, y):
  """Subtract y from x."""
  return x - y


@pipeable
def divide(x, divisor):
  """Divide x by divisor."""
  if divisor == 0:
    raise ValueError("Cannot divide by zero")
  return x / divisor


@pipeable
def append_string(x, suffix):
  """Append a string suffix."""
  return f"{x}{suffix}"


@pipeable
def to_upper(x):
  """Convert to uppercase."""
  return str(x).upper()


@pipeable
def identity(x):
  """Return the input unchanged."""
  return x


@pipeable
def add_with_kwargs(x, y=1, z=0):
  """Add with optional keyword arguments."""
  return x + y + z


class TestBasicPipeline:
  """Test basic pipeline operations."""
  
  def test_simple_pipeline(self):
    """Test basic pipeline with two functions."""
    result = 5 | add(3) | multiply(2)
    assert result == 16
    
  def test_longer_pipeline(self):
    """Test pipeline with multiple operations."""
    result = 10 | add(5) | multiply(3) | subtract(10) | divide(5)
    assert result == 7.0
    
  def test_single_function_pipeline(self):
    """Test pipeline with just one function."""
    result = 42 | identity
    assert result == 42
  
  def test_pipeline_with_different_types(self):
    """Test pipeline that transforms types."""
    # Need to wrap built-in types with pipeable
    result = 5 | add(10) | pipeable(str) | append_string(" items") | to_upper
    assert result == "15 ITEMS"


class TestPartialApplication:
  """Test partial application functionality."""
  
  def test_partial_application(self):
    """Test creating partial functions."""
    add_five = add(5)
    result = 10 | add_five
    assert result == 15
    
  def test_multiple_partial_applications(self):
    """Test chaining partial applications."""
    add_three = add(3)
    times_two = multiply(2)
    
    result = 5 | add_three | times_two
    assert result == 16
    
  def test_partial_with_multiple_args(self):
    """Test partial application preserves argument order."""
    subtract_from_ten = subtract(10)  # This binds y=10, so x | subtract_from_ten = x - 10
    result = 3 | subtract_from_ten
    assert result == -7  # 3 - 10 = -7
    
  def test_partial_with_kwargs(self):
    """Test partial application with keyword arguments."""
    add_with_defaults = add_with_kwargs(y=5, z=2)
    result = 10 | add_with_defaults
    assert result == 17  # 10 + 5 + 2


class TestDirectCalls:
  """Test calling pipeable functions directly."""
  
  def test_direct_call(self):
    """Test that pipeable functions can still be called directly."""
    result = add(5, 3)
    assert result == 8
    
  def test_direct_call_preserves_metadata(self):
    """Test that function metadata is preserved."""
    assert add.__name__ == 'add'
    assert add.__doc__ == 'Add two numbers.'
    
  def test_direct_call_with_kwargs(self):
    """Test direct calls with keyword arguments."""
    result = add_with_kwargs(10, y=5, z=3)
    assert result == 18


class TestErrorHandling:
  """Test error handling in pipelines."""
  
  def test_error_in_pipeline(self):
    """Test that errors propagate correctly."""
    with pytest.raises(ValueError, match="Cannot divide by zero"):
      5 | add(5) | divide(0)
      
  def test_type_error_wrong_args(self):
    """Test appropriate error for wrong number of arguments."""
    with pytest.raises(TypeError):
      5 | add  # add needs 2 args, only gets 1
      
  def test_invalid_pipeline_start(self):
    """Test error when pipeline doesn't start with a value."""
    with pytest.raises(TypeError, match="Cannot pipe .* directly to"):
      add(5) | multiply(2)  # This creates add(5) | multiply(2), not a value pipeline
      
  def test_result_not_pipeable(self):
    """Test that function results are not Pipeable objects."""
    # When calling a pipeable function with all required args,
    # it should return the actual result, not a Pipeable
    result = add(1, 2)
    assert result == 3
    assert not isinstance(result, Pipeable)


class TestRepresentation:
  """Test string representation of Pipeable objects."""
  
  def test_simple_pipeable_repr(self):
    """Test repr of pipeable without bound args."""
    assert repr(add) == 'Pipeable(add)'
    
  def test_partial_pipeable_repr(self):
    """Test repr of pipeable with bound args."""
    partial = add(5)
    assert repr(partial) == 'Pipeable(add(5))'
    
  def test_partial_with_kwargs_repr(self):
    """Test repr of pipeable with bound kwargs."""
    # Create a function that requires multiple args to test partial repr
    @pipeable
    def requires_three_args(a, b, c):
      return a + b + c
    
    # Create partial with some kwargs bound
    partial = requires_three_args(5, c=3)
    assert repr(partial) == "Pipeable(requires_three_args(5, c=3))"


class TestComplexScenarios:
  """Test more complex pipeline scenarios."""
  
  def test_nested_function_calls(self):
    """Test pipelines with nested function calls."""
    # Create a more complex pipeline
    result = 5 | add(multiply(2, 3)) | divide(2)
    # 5 + (2 * 3) = 11, then 11 / 2 = 5.5
    assert result == 5.5
    
  def test_pipeline_in_function(self):
    """Test using pipelines inside regular functions."""
    def process_number(n):
      return n | add(10) | multiply(2) | subtract(5)
    
    assert process_number(5) == 25  # (5 + 10) * 2 - 5 = 25
    
  def test_storing_pipeline_result(self):
    """Test storing intermediate pipeline results."""
    intermediate = 5 | add(3)
    assert intermediate == 8
    
    final = intermediate | multiply(2)
    assert final == 16
    
  def test_reusing_partials(self):
    """Test that partial applications can be reused."""
    add_ten = add(10)
    
    result1 = 5 | add_ten
    result2 = 20 | add_ten  
    
    assert result1 == 15
    assert result2 == 30