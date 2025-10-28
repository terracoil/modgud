"""Performance benchmarks for guard evaluation."""

import time

from modgud import CommonGuards, guarded_expression


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
