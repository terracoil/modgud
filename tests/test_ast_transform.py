"""Unit tests for AST transformation logic."""
import ast

import pytest
from modgud.guarded_expression.ast_transform import apply_implicit_return_transform
from modgud.shared.errors import ExplicitReturnDisallowedError, MissingImplicitReturnError


def test_simple_expression_transform():
  """Test transformation of simple expression."""
  source = """
def foo():
    x = 10
    x + 5
"""
  tree, filename = apply_implicit_return_transform(source.strip(), "foo")
  assert isinstance(tree, ast.Module)
  assert filename == "<foo-implicit>"


def test_if_else_transform():
  """Test transformation of if/else statement."""
  source = """
def foo(x):
    if x > 0:
        "positive"
    else:
        "negative"
"""
  tree, _ = apply_implicit_return_transform(source.strip(), "foo")
  assert isinstance(tree, ast.Module)


def test_try_except_transform():
  """Test transformation of try/except statement."""
  source = """
def foo(x):
    try:
        x / 2
    except ZeroDivisionError:
        0
"""
  tree, _ = apply_implicit_return_transform(source.strip(), "foo")
  assert isinstance(tree, ast.Module)


def test_explicit_return_raises_error():
  """Test that explicit return raises error."""
  source = """
def foo():
    return 10
"""
  with pytest.raises(ExplicitReturnDisallowedError):
    apply_implicit_return_transform(source.strip(), "foo")


def test_if_without_else_raises_error():
  """Test that if without else at tail raises error."""
  source = """
def foo(x):
    if x > 0:
        "positive"
"""
  with pytest.raises(MissingImplicitReturnError):
    apply_implicit_return_transform(source.strip(), "foo")


def test_empty_block_raises_error():
  """Test that empty block raises error."""
  source = """
def foo():
    pass
"""
  with pytest.raises(MissingImplicitReturnError):
    apply_implicit_return_transform(source.strip(), "foo")


def test_nested_function_allows_return():
  """Test that nested functions can use return statements."""
  source = """
def outer():
    def inner():
        return 10
    x = inner()
    x + 5
"""
  tree, _ = apply_implicit_return_transform(source.strip(), "outer")
  assert isinstance(tree, ast.Module)
