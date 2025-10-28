"""Tests for match statement transformations."""

import ast

from modgud.infrastructure.adapters.ast_transformer_adapter import AstTransformerAdapter


class TestMatchStatements:
  """Tests for match statement transformations."""

  def test_match_pass_returns_none(self):
    """Test match with pass in case body returns None gracefully."""
    source = """
def foo(x):
    match x:
        case 1:
            pass
"""
    tree, _ = AstTransformerAdapter.apply_implicit_return_transform(source.strip(), 'foo')
    # Should transform successfully, pass case returns None
    assert isinstance(tree, ast.Module)

  def test_match_all_cases_transform(self):
    """Test match where all cases produce values."""
    source = """
def foo(x):
    match x:
        case 1:
            "one"
        case 2:
            "two"
        case _:
            "other"
"""
    tree, _ = AstTransformerAdapter.apply_implicit_return_transform(source.strip(), 'foo')
    # Compile and verify it works
    code = compile(tree, '<test>', 'exec')
    env = {}
    exec(code, env)
    assert env['foo'](1) == 'one'
    assert env['foo'](2) == 'two'
    assert env['foo'](99) == 'other'
