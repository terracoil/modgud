"""Tests for metadata preservation and edge cases."""

import pytest
from modgud.guarded_expression import guarded_expression
from modgud.guarded_expression.errors import GuardClauseError, UnsupportedConstructError


def test_metadata_preservation():
  """Function metadata should be preserved after decoration."""

  @guarded_expression(implicit_return=False, on_error=GuardClauseError)
  def documented_function(x: int) -> int:
    """Multiply input by two."""
    return x * 2

  assert documented_function.__name__ == 'documented_function'
  assert documented_function.__doc__ == 'Multiply input by two.'
  assert documented_function.__annotations__ == {'x': int, 'return': int}


def test_no_guards_implicit_return_false():
  """Decorator should work with no guards and implicit_return=False."""

  @guarded_expression(implicit_return=False, on_error=GuardClauseError)
  def simple(x):
    return x * 2

  assert simple(5) == 10


def test_no_guards_implicit_return_true():
  """Decorator should work with no guards and implicit_return=True."""
  from tests.test_fixtures import simple_implicit

  assert simple_implicit(5) == 10


def test_decorator_source_unavailable():
  """Decorator should fail gracefully when source code is unavailable."""
  # Create function from compiled code
  code = compile('def foo(): return 42', '<string>', 'exec')
  env = {}
  exec(code, env)

  with pytest.raises(UnsupportedConstructError, match='Source unavailable'):
    guarded_expression(implicit_return=True)(env['foo'])
