"""Tests for complex try-except-else-finally transformations."""

import ast

from modgud.infrastructure.adapters.ast_transformer_adapter import AstTransformerAdapter


class TestComplexTryStatements:
  """Tests for complex try-except-else-finally transformations."""

  def test_try_except_else_finally_transform(self):
    """Test try-except-else-finally with all branches setting result."""
    source = """
def foo(x):
    try:
        10 / x
    except ZeroDivisionError:
        0
    else:
        x + 1
    finally:
        pass
"""
    tree, _ = AstTransformerAdapter.apply_implicit_return_transform(source.strip(), 'foo')
    assert isinstance(tree, ast.Module)
    # Verify it compiles and works
    code = compile(tree, '<test>', 'exec')
    env = {}
    exec(code, env)
    assert env['foo'](2) == 3  # No exception, try succeeds (10/2=5), else runs (2+1=3)
    assert env['foo'](0) == 0  # Exception caught, except block returns 0
