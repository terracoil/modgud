"""Tests for decorator edge cases and error conditions."""

import pytest
from modgud import guarded_expression
from modgud.domain.models.errors import UnsupportedConstructError


class TestDecoratorEdgeCases:
  """Tests for decorator edge cases and error conditions."""

  def test_decorator_source_unavailable(self):
    """Decorator should fail gracefully when source code is unavailable."""
    # Create function from compiled code
    code = compile('def foo(): return 42', '<string>', 'exec')
    env = {}
    exec(code, env)

    with pytest.raises(UnsupportedConstructError, match='Source unavailable'):
      guarded_expression(implicit_return=True)(env['foo'])
