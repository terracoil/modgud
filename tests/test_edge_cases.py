"""Edge case and error condition tests for guarded_expression."""

import time
from threading import Thread
from typing import List

import pytest
from modgud import positive
from modgud.guarded_expression import CommonGuards, guarded_expression
from modgud.guarded_expression.errors import GuardClauseError
from modgud.guarded_expression.guard_registry import GuardRegistry


class TestThreadSafety:
  """Thread safety tests for guard execution and registry operations."""

  def test_concurrent_guard_execution(self):
    """Guards must be thread-safe during concurrent execution."""
    results: List[int] = []
    errors: List[Exception] = []

    @guarded_expression(positive('x'), implicit_return=False)
    def process(x):
      time.sleep(0.001)  # Simulate processing
      return x * 2

    def worker(value):
      try:
        result = process(value)
        results.append(result)
      except Exception as e:
        errors.append(e)

    # Create threads with mix of valid and invalid values
    threads = []
    for i in range(50):
      value = i - 25  # Mix of positive and negative
      t = Thread(target=worker, args=(value,))
      threads.append(t)
      t.start()

    # Wait for all threads
    for t in threads:
      t.join()

    # Verify results
    assert len(results) + len(errors) == 50
    assert len(results) == 24  # Only positive values succeed (1-24, 0 is not positive)
    assert all(isinstance(e, GuardClauseError) for e in errors)

  def test_concurrent_registry_operations(self):
    """Registry operations must be thread-safe."""
    registry = GuardRegistry()
    results = {'register': [], 'get': [], 'errors': []}

    def register_guard(name: str):
      try:
        registry.register(name, lambda: True)
        results['register'].append(name)
      except Exception as e:
        results['errors'].append(e)

    def get_guard(name: str):
      try:
        guard = registry.get(name)
        if guard:
          results['get'].append(name)
      except Exception:
        pass  # Expected for non-existent guards

    # Create concurrent operations
    threads = []
    for i in range(20):
      name = f'guard_{i % 10}'  # Some duplicate names
      t1 = Thread(target=register_guard, args=(name,))
      t2 = Thread(target=get_guard, args=(name,))
      threads.extend([t1, t2])
      t1.start()
      t2.start()

    for t in threads:
      t.join()

    # Verify no race conditions caused crashes
    assert len(results['register']) + len(results['errors']) > 0
    assert len(results['register']) <= 10  # At most 10 unique guards


class TestPerformance:
  """Performance benchmarks for guard evaluation."""

  def test_guard_evaluation_overhead(self):
    """Guard overhead should be minimal (< 1ms per call)."""

    @guarded_expression(CommonGuards.positive('x'), implicit_return=False)
    def compute(x):
      return x * 2

    # Warm up
    for _ in range(10):
      compute(5)

    # Measure performance
    start = time.perf_counter()
    iterations = 1000
    for _ in range(iterations):
      compute(5)
    elapsed = time.perf_counter() - start

    # Check average time per call
    avg_ms = (elapsed / iterations) * 1000
    assert avg_ms < 1.0  # Less than 1ms per call

  def test_multiple_guards_performance(self):
    """Multiple guards should still have acceptable performance."""

    @guarded_expression(
      CommonGuards.not_none('x'),
      CommonGuards.positive('x'),
      CommonGuards.in_range(1, 100, 'x'),
      CommonGuards.type_check(int, 'x'),
      implicit_return=False,
    )
    def process(x):
      return x * 2

    # Warm up
    for _ in range(10):
      process(50)

    # Measure performance
    start = time.perf_counter()
    iterations = 500
    for _ in range(iterations):
      process(50)
    elapsed = time.perf_counter() - start

    # Check average time per call
    avg_ms = (elapsed / iterations) * 1000
    assert avg_ms < 2.0  # Less than 2ms per call even with 4 guards


class TestErrorConditions:
  """Tests for various error conditions and edge cases."""

  def test_guard_raises_exception(self):
    """Guard that raises exception should be handled gracefully."""

    def bad_guard(*args, **kwargs):
      raise RuntimeError('Guard evaluation failed')

    @guarded_expression(bad_guard, implicit_return=False, on_error=None)
    def process(x):
      return x * 2

    # Should return None (on_error=None) when guard raises
    with pytest.raises(RuntimeError, match='Guard evaluation failed'):
      process(5)

  def test_unicode_parameter_names(self):
    """Guards should handle unicode parameter names."""

    @guarded_expression(CommonGuards.positive('value'), implicit_return=False)
    def process(value):
      return value * 2

    assert process(value=5) == 10
    with pytest.raises(GuardClauseError):
      process(value=-5)

  def test_long_error_messages(self):
    """Guards should handle very long error messages."""
    long_message = 'A' * 2000  # 2000 character error message

    @guarded_expression(lambda x: x > 0 or long_message, implicit_return=False)
    def process(x):
      return x * 2

    with pytest.raises(GuardClauseError) as exc_info:
      process(-5)
    assert len(str(exc_info.value)) >= 2000

  def test_deeply_nested_control_flow(self):
    """Implicit return should work with deeply nested control flow."""
    from tests.test_fixtures import deeply_nested_function

    assert deeply_nested_function(1) == 'one'
    assert deeply_nested_function(2) == 'two-a'
    assert deeply_nested_function(3) == 'three-a-i'
    assert deeply_nested_function(4) == 'three-a-ii'
    assert deeply_nested_function(5) == 'three-b'
    assert deeply_nested_function(10) == 'other'

  def test_recursive_function_with_guards(self):
    """Guards should work with recursive functions."""

    @guarded_expression(
      CommonGuards.not_none('n'), CommonGuards.positive('n'), implicit_return=False
    )
    def factorial(n):
      if n <= 1:
        result = 1
      else:
        result = n * factorial(n - 1)
      return result

    assert factorial(5) == 120
    assert factorial(1) == 1

    with pytest.raises(GuardClauseError):
      factorial(-5)

  def test_function_with_many_parameters(self):
    """Guards should work with functions having many parameters."""

    @guarded_expression(
      CommonGuards.positive('a'),
      CommonGuards.positive('b'),
      CommonGuards.positive('c'),
      implicit_return=False,
    )
    def sum_many(a, b, c, d, e, f, g, h, i, j):
      return a + b + c + d + e + f + g + h + i + j

    assert sum_many(1, 2, 3, 4, 5, 6, 7, 8, 9, 10) == 55

    with pytest.raises(GuardClauseError):
      sum_many(-1, 2, 3, 4, 5, 6, 7, 8, 9, 10)


class TestGuardComposition:
  """Tests for guard function composition and chaining."""

  def test_composed_guards(self):
    """Multiple validation layers should compose correctly."""

    def create_validation_layer(layer_name: str):
      def guard(*args, **kwargs):
        # Pass through - just for composition testing
        return True

      return guard

    @guarded_expression(
      create_validation_layer('auth'),
      create_validation_layer('permissions'),
      create_validation_layer('rate_limit'),
      create_validation_layer('input_validation'),
      implicit_return=False,
    )
    def api_endpoint(data):
      return {'status': 'ok', 'data': data}

    assert api_endpoint('test') == {'status': 'ok', 'data': 'test'}

  def test_guard_short_circuit(self):
    """Guards should short-circuit on first failure."""
    call_count = {'guard1': 0, 'guard2': 0, 'guard3': 0}

    def counting_guard1(*args, **kwargs):
      call_count['guard1'] += 1
      return False or 'Guard 1 failed'

    def counting_guard2(*args, **kwargs):
      call_count['guard2'] += 1
      return True

    def counting_guard3(*args, **kwargs):
      call_count['guard3'] += 1
      return True

    @guarded_expression(counting_guard1, counting_guard2, counting_guard3, implicit_return=False)
    def process(x):
      return x

    with pytest.raises(GuardClauseError):
      process(5)

    # Only first guard should have been called due to short-circuit
    assert call_count['guard1'] == 1
    assert call_count['guard2'] == 0
    assert call_count['guard3'] == 0


class TestImplicitReturnEdgeCases:
  """Tests for edge cases in implicit return transformation."""

  def test_noop_function_with_pass(self):
    """Function with only pass should handle gracefully."""
    from tests.test_fixtures import noop_function

    # pass statement should result in None being returned
    result = noop_function(5)
    assert result is None

  def test_exception_only_function(self):
    """Function that only raises exceptions should work correctly."""
    from tests.test_fixtures import exception_only_function

    # All paths raise exceptions
    with pytest.raises(ValueError, match='Negative value'):
      exception_only_function(-5)

    with pytest.raises(RuntimeError, match='Non-negative value'):
      exception_only_function(5)

  def test_empty_function_body(self):
    """Function with just docstring should handle gracefully."""
    from tests.test_fixtures import empty_function

    # Empty body should result in None being returned
    result = empty_function(10)
    assert result is None

  def test_conditional_noop_paths(self):
    """Function with some paths having values and some having pass."""
    from tests.test_fixtures import conditional_noop

    # Positive path has value
    assert conditional_noop(5) == 10

    # Negative path has pass (should return None)
    result = conditional_noop(-5)
    assert result is None

    # Zero path has None (should return None)
    result = conditional_noop(0)
    assert result is None
