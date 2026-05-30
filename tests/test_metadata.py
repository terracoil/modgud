"""Tests for metadata preservation and edge cases."""

import pytest
from modgud import guarded_expression


class TestMetadataPreservation:
  """Tests for function metadata preservation through decoration."""

  def test_metadata_preservation(self):
    """Function metadata should be preserved after decoration."""

    @guarded_expression(implicit_return=False)
    def documented_function(x: int) -> int:
      """Multiply input by two."""
      return x * 2

    assert documented_function.__name__ == 'documented_function'
    assert documented_function.__doc__ == 'Multiply input by two.'
    assert documented_function.__annotations__ == {'x': int, 'return': int}


class TestDecoratorWithoutGuards:
  """Tests for decorator behavior when no guards are provided."""

  def test_no_guards_implicit_return_false(self):
    """Decorator should work with no guards and implicit_return=False."""

    @guarded_expression(implicit_return=False)
    def simple(x):
      return x * 2

    assert simple(5) == 10

  def test_no_guards_implicit_return_true(self):
    """Decorator should work with no guards and implicit_return=True."""
    from tests.test_fixtures import simple_implicit

    assert simple_implicit(5) == 10


class TestDecoratorEdgeCases:
  """Tests for decorator edge cases and error conditions."""

  def test_decorator_raises_on_unavailable_source_with_implicit_return(self):
    """Strict mode: decoration raises when source can't be extracted and implicit_return=True."""
    code = compile('def foo(): return 42', '<string>', 'exec')
    env: dict = {}
    exec(code, env)
    with pytest.raises((ValueError, OSError)):
      guarded_expression(implicit_return=True)(env['foo'])

  def test_decorator_skips_transform_when_implicit_return_false(self):
    """Source unavailability is irrelevant when implicit_return is disabled."""
    code = compile('def foo(): return 42', '<string>', 'exec')
    env: dict = {}
    exec(code, env)
    decorated = guarded_expression(implicit_return=False)(env['foo'])
    assert decorated() == 42
