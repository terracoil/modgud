"""Tests for async function support in guarded_expression."""

import asyncio

import pytest
from modgud import GuardClauseError

from tests.test_fixtures import (
  async_classify,
  async_double,
  async_explicit_return,
  async_with_fallback,
)


class TestAsyncFunctionSupport:
  """Tests for async function compatibility with guards and implicit returns."""

  def test_async_with_guards_and_implicit_return(self):
    """Async functions should work with guards and implicit return."""
    # Test success
    assert asyncio.run(async_double(5)) == 10

    # Test guard failure
    with pytest.raises(GuardClauseError):
      asyncio.run(async_double(-5))

  def test_async_implicit_return_with_branching(self):
    """Async functions should handle implicit return with if/else."""
    assert asyncio.run(async_classify(5)) == 'positive'
    assert asyncio.run(async_classify(-5)) == 'non-positive'

  def test_async_explicit_return(self):
    """Async functions should work with explicit return when implicit_return=False."""
    assert asyncio.run(async_explicit_return(5)) == 15


class TestAsyncFallbackStrategies:
  def test_non_raising_strategy_returns_the_fallback_from_await(self):
    assert asyncio.run(async_with_fallback(2)) == 4
    assert asyncio.run(async_with_fallback(-2)) == 'fallback'
