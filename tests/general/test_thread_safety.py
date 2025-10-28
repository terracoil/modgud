"""Thread safety tests for guard execution and registry operations."""

import time
from threading import Thread
from typing import List

from modgud import guarded_expression, positive
from modgud.domain.models.errors import GuardClauseError
from modgud.surface.registry import GuardRegistry


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
    registry = GuardRegistry._create_for_testing()
    results = {'register': [], 'get': [], 'errors': []}

    def register_guard(name: str):
      try:
        registry._register(name, lambda: True)
        results['register'].append(name)
      except Exception as e:
        results['errors'].append(e)

    def get_guard(name: str):
      try:
        guard = registry._get(name)
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
