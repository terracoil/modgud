"""Tests for basic AST transformations of common patterns."""

import ast

from modgud.infrastructure.adapters.ast_transformer_adapter import AstTransformerAdapter


class TestBasicTransformations:
  """Tests for basic AST transformations of common patterns."""

  def test_simple_expression_transform(self):
    """Test transformation of simple expression."""
    source = """
def foo():
    x = 10
    x + 5
"""
    tree, filename = AstTransformerAdapter.apply_implicit_return_transform(source.strip(), 'foo')
    assert isinstance(tree, ast.Module)
    assert filename == '<foo-implicit>'

  def test_if_else_transform(self):
    """Test transformation of if/else statement."""
    source = """
def foo(x):
    if x > 0:
        "positive"
    else:
        "negative"
"""
    tree, _ = AstTransformerAdapter.apply_implicit_return_transform(source.strip(), 'foo')
    assert isinstance(tree, ast.Module)

  def test_try_except_transform(self):
    """Test transformation of try/except statement."""
    source = """
def foo(x):
    try:
        x / 2
    except ZeroDivisionError:
        0
"""
    tree, _ = AstTransformerAdapter.apply_implicit_return_transform(source.strip(), 'foo')
    assert isinstance(tree, ast.Module)
