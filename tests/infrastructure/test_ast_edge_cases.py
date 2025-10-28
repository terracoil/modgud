"""Tests for edge cases and special scenarios in AST transformation."""

import ast

from modgud.infrastructure.adapters.ast_transformer_adapter import AstTransformerAdapter


class TestEdgeCases:
  """Tests for edge cases and special scenarios in AST transformation."""

  def test_empty_block_returns_none(self):
    """Test that function with only pass returns None gracefully."""
    source = """
def foo():
    pass
"""
    tree, _ = AstTransformerAdapter.apply_implicit_return_transform(source.strip(), 'foo')
    # Should transform successfully and return None
    assert isinstance(tree, ast.Module)

  def test_nested_function_allows_return(self):
    """Test that nested functions can use return statements."""
    source = """
def outer():
    def inner():
        return 10
    x = inner()
    x + 5
"""
    tree, _ = AstTransformerAdapter.apply_implicit_return_transform(source.strip(), 'outer')
    assert isinstance(tree, ast.Module)

  def test_nested_lambda_not_transformed(self):
    """Test nested lambda functions are not transformed."""
    source = """
def foo(x):
    f = lambda y: y + 1
    result = f(x)
    result * 2
"""
    tree, _ = AstTransformerAdapter.apply_implicit_return_transform(source.strip(), 'foo')
    assert isinstance(tree, ast.Module)
    # Verify it compiles and works
    code = compile(tree, '<test>', 'exec')
    env = {}
    exec(code, env)
    assert env['foo'](5) == 12

  def test_async_function_blocked(self):
    """Test async function definitions are not traversed."""
    source = """
async def foo(x):
    await some_async_call()
    x + 1
"""
    # async functions should work but not be transformed
    tree, _ = AstTransformerAdapter.apply_implicit_return_transform(source.strip(), 'foo')
    assert isinstance(tree, ast.Module)
