"""Tests for async function compatibility with guards and implicit returns."""

import asyncio

import pytest
from modgud.domain.models.errors import GuardClauseError


class TestAsyncFunctionSupport:
  """Tests for async function compatibility with guards and implicit returns."""

  def test_async_with_guards_and_implicit_return(self):
    """Async functions should work with guards and implicit return."""
    from tests.helpers import async_double

    # Test success
    assert asyncio.run(async_double(5)) == 10

    # Test guard failure
    with pytest.raises(GuardClauseError):
      asyncio.run(async_double(-5))

  def test_async_implicit_return_with_branching(self):
    """Async functions should handle implicit return with if/else."""
    from tests.helpers import async_classify

    assert asyncio.run(async_classify(5)) == 'positive'
    assert asyncio.run(async_classify(-5)) == 'non-positive'

  def test_async_explicit_return(self):
    """Async functions should work with explicit return when implicit_return=False."""
    from tests.helpers import async_explicit_return

    assert asyncio.run(async_explicit_return(5)) == 15
