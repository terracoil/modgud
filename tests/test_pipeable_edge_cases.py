"""Test edge cases and thread safety for @pipeable decorator."""

import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest
from modgud import guarded_expression, implicit_return, pipeable, positive


# Test functions for edge cases
@pipeable
def slow_add(x, y, delay=0.01):
  """Add with artificial delay for thread testing."""
  time.sleep(delay)
  return x + y


@pipeable
def stateful_counter():
  """A stateful function to test thread safety."""
  if not hasattr(stateful_counter, '_count'):
    stateful_counter._count = 0
  stateful_counter._count += 1
  return stateful_counter._count


@pipeable
def no_args():
  """Function with no arguments."""
  return 42


@pipeable
def many_args(a, b, c, d, e, f):
  """Function with many arguments."""
  return a + b + c + d + e + f


@pipeable
def with_varargs(x, *args, **kwargs):
  """Function with variable arguments."""
  total = x
  for arg in args:
    total += arg
  for value in kwargs.values():
    total += value
  return total


@pipeable
def returns_pipeable(x):
  """Function that returns another pipeable function."""

  @pipeable
  def inner(y):
    return x + y

  return inner


@pipeable
def recursive_factorial(n):
  """Recursive function to test stack behavior."""
  if n <= 1:
    return 1
  return n * recursive_factorial.func(n - 1)


class CustomClass:
  """Custom class to test with pipeable."""

  def __init__(self, value):
    self.value = value

  @pipeable
  def add_method(self, x):
    """Instance method as pipeable."""
    return CustomClass(self.value + x)

  def __repr__(self):
    return f'CustomClass({self.value})'


class TestEdgeCases:
  """Test edge cases for pipeable decorator."""

  def test_no_arguments_function(self):
    """Test function with no arguments."""
    # Direct call
    assert no_args() == 42

    # Pipeline into no-args function ignores piped value
    result = 5 | no_args
    assert result == 42

  def test_many_arguments_partial(self):
    """Test partial application with many arguments."""
    # Create multiple partial applications
    partial1 = many_args(1, 2, 3)
    partial2 = partial1(4, 5)

    # Final application
    result = 6 | partial2
    assert result == 21  # 1+2+3+4+5+6

  def test_varargs_and_kwargs(self):
    """Test functions with *args and **kwargs."""
    result = 10 | with_varargs(5, 3, x=2, y=4)
    assert result == 24  # 10+5+3+2+4

  def test_nested_pipeable_returns(self):
    """Test functions that return pipeable functions."""
    add_five = 5 | returns_pipeable
    result = 10 | add_five
    assert result == 15

  def test_recursive_function(self):
    """Test recursive pipeable functions."""
    result = 5 | recursive_factorial
    assert result == 120

  def test_method_as_pipeable(self):
    """Test instance methods decorated with @pipeable."""
    obj = CustomClass(10)
    result = 5 | obj.add_method
    assert result.value == 15

  def test_empty_pipeline(self):
    """Test behavior with empty/null values."""
    # Test with 0 instead of None, since None + 5 doesn't work in Python
    assert 0 | slow_add(5) == 5  # Should work, 0 + 5 = 5
    
    # Test that None still gets passed through (will raise TypeError as expected)
    with pytest.raises(TypeError):
      None | slow_add(5)

  def test_exception_in_partial(self):
    """Test exception handling in partial applications."""

    @pipeable
    def may_fail(x, fail=False):
      if fail:
        raise ValueError('Intentional failure')
      return x * 2

    fail_partial = may_fail(fail=True)

    with pytest.raises(ValueError, match='Intentional failure'):
      5 | fail_partial


class TestThreadSafety:
  """Test thread safety of pipeable decorators."""

  def test_concurrent_pipeline_execution(self):
    """Test multiple threads executing pipelines concurrently."""
    results = []
    errors = []

    def run_pipeline(value):
      try:
        result = value | slow_add(10) | slow_add(20) | slow_add(30)
        results.append(result)
      except Exception as e:
        errors.append(e)

    # Run pipelines in multiple threads
    threads = []
    for i in range(10):
      thread = threading.Thread(target=run_pipeline, args=(i,))
      threads.append(thread)
      thread.start()

    # Wait for all threads
    for thread in threads:
      thread.join()

    # Verify results
    assert len(errors) == 0
    assert len(results) == 10
    # Each result should be input + 60
    for i, result in enumerate(sorted(results)):
      assert result == i + 60

  def test_partial_application_thread_safety(self):
    """Test that partial applications are thread-safe."""
    add_hundred = slow_add(100)
    results = []

    def use_partial(value):
      result = value | add_hundred
      results.append(result)

    # Use the same partial in multiple threads
    with ThreadPoolExecutor(max_workers=5) as executor:
      futures = [executor.submit(use_partial, i) for i in range(20)]
      for future in futures:
        future.result()

    # Verify all results are correct
    assert len(results) == 20
    assert sorted(results) == [i + 100 for i in range(20)]

  def test_decorator_state_isolation(self):
    """Test that decorator state is isolated between instances."""
    # Reset counter
    if hasattr(stateful_counter, '_count'):
      del stateful_counter._count

    results = []

    def count_in_thread():
      # Each thread does 5 counts
      thread_results = []
      for _ in range(5):
        result = 0 | stateful_counter
        thread_results.append(result)
      results.append(thread_results)

    # Run in multiple threads
    threads = []
    for _ in range(3):
      thread = threading.Thread(target=count_in_thread)
      threads.append(thread)
      thread.start()

    for thread in threads:
      thread.join()

    # Collect all counts
    all_counts = []
    for thread_results in results:
      all_counts.extend(thread_results)

    # Should have counts 1-15 (not necessarily in order due to threading)
    assert sorted(all_counts) == list(range(1, 16))


class TestComplexEdgeCases:
  """Test complex edge cases and unusual usage patterns."""

  def test_pipeline_with_side_effects(self):
    """Test pipeline with functions that have side effects."""
    side_effects = []

    @pipeable
    def track_value(x, label):
      side_effects.append((label, x))
      return x

    result = (
      5
      | track_value('start')
      | slow_add(3)
      | track_value('middle')
      | slow_add(2)
      | track_value('end')
    )

    assert result == 10
    assert side_effects == [('start', 5), ('middle', 8), ('end', 10)]

  def test_very_long_pipeline(self):
    """Test performance with very long pipelines."""

    @pipeable
    def increment(x):
      return x + 1

    # Build a very long pipeline
    value = 0
    for _ in range(100):
      value = value | increment

    assert value == 100

  def test_pipeable_with_decorators_stacked(self):
    """Test pipeable with other decorators stacked."""
    call_count = 0

    def count_calls(func):
      def wrapper(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        return func(*args, **kwargs)

      return wrapper

    @pipeable
    @count_calls
    def monitored_add(x, y):
      return x + y

    result = 5 | monitored_add(3) | monitored_add(2)
    assert result == 10
    assert call_count == 2

  def test_generator_in_pipeline(self):
    """Test using generators with pipeable."""

    @pipeable
    def sum_generator(x, gen):
      """Sum a generator with initial value."""
      return x + sum(gen)

    def make_gen(n):
      for i in range(n):
        yield i

    result = 10 | sum_generator(make_gen(5))
    assert result == 20  # 10 + (0+1+2+3+4)

  def test_class_decorator_interaction(self):
    """Test pipeable on class methods with other decorators."""

    class Calculator:
      def __init__(self):
        self.call_log = []

      @pipeable
      @guarded_expression(positive('x', 1), implicit_return=False)
      def safe_sqrt(self, x):
        """Calculate square root with validation."""
        self.call_log.append(f'sqrt({x})')
        return x**0.5

      @pipeable
      @implicit_return
      def double(self, x):
        """Double the value."""
        self.call_log.append(f'double({x})')
        x * 2

    calc = Calculator()
    result = 16 | calc.safe_sqrt | calc.double

    assert result == 8.0  # sqrt(16) = 4, double(4) = 8
    assert calc.call_log == ['sqrt(16)', 'double(4.0)']

    # Test guard validation
    with pytest.raises(Exception):  # GuardClauseError
      -16 | calc.safe_sqrt
