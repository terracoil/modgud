"""Unit tests for AST transformation logic."""

import ast

import pytest
from modgud.domain.exceptions import (
  ExplicitReturnDisallowedError,
  MissingImplicitReturnError,
)
from modgud.infrastructure.implicit_return import ImplicitReturnTransformer


class TestBasicTransformations:
  """Tests for basic AST transformations of common patterns."""

  def test_simple_expression_transform(self):
    """Test transformation of simple expression."""
    source = """
def foo():
    x = 10
    x + 5
"""
    tree, filename = ImplicitReturnTransformer.apply_implicit_return_transform(
      source.strip(), 'foo'
    )
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
    tree, _ = ImplicitReturnTransformer.apply_implicit_return_transform(source.strip(), 'foo')
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
    tree, _ = ImplicitReturnTransformer.apply_implicit_return_transform(source.strip(), 'foo')
    assert isinstance(tree, ast.Module)


class TestTransformationErrors:
  """Tests for error conditions during AST transformation."""

  def test_explicit_return_raises_error(self):
    """Test that explicit return raises error."""
    source = """
def foo():
    return 10
"""
    with pytest.raises(ExplicitReturnDisallowedError):
      ImplicitReturnTransformer.apply_implicit_return_transform(source.strip(), 'foo')

  def test_if_without_else_raises_error(self):
    """Test that if without else at tail raises error."""
    source = """
def foo(x):
    if x > 0:
        "positive"
"""
    with pytest.raises(MissingImplicitReturnError):
      ImplicitReturnTransformer.apply_implicit_return_transform(source.strip(), 'foo')


class TestEdgeCases:
  """Tests for edge cases and special scenarios in AST transformation."""

  def test_empty_block_returns_none(self):
    """Test that function with only pass returns None gracefully."""
    source = """
def foo():
    pass
"""
    tree, _ = ImplicitReturnTransformer.apply_implicit_return_transform(source.strip(), 'foo')
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
    tree, _ = ImplicitReturnTransformer.apply_implicit_return_transform(source.strip(), 'outer')
    assert isinstance(tree, ast.Module)

  def test_nested_lambda_not_transformed(self):
    """Test nested lambda functions are not transformed."""
    source = """
def foo(x):
    f = lambda y: y + 1
    result = f(x)
    result * 2
"""
    tree, _ = ImplicitReturnTransformer.apply_implicit_return_transform(source.strip(), 'foo')
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
    tree, _ = ImplicitReturnTransformer.apply_implicit_return_transform(source.strip(), 'foo')
    assert isinstance(tree, ast.Module)


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
    tree, _ = ImplicitReturnTransformer.apply_implicit_return_transform(source.strip(), 'foo')
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
    tree, _ = ImplicitReturnTransformer.apply_implicit_return_transform(source.strip(), 'foo')
    # Compile and verify it works
    code = compile(tree, '<test>', 'exec')
    env = {}
    exec(code, env)
    assert env['foo'](1) == 'one'
    assert env['foo'](2) == 'two'
    assert env['foo'](99) == 'other'


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
    tree, _ = ImplicitReturnTransformer.apply_implicit_return_transform(source.strip(), 'foo')
    assert isinstance(tree, ast.Module)
    # Verify it compiles and works
    code = compile(tree, '<test>', 'exec')
    env = {}
    exec(code, env)
    assert env['foo'](2) == 3  # No exception, try succeeds (10/2=5), else runs (2+1=3)
    assert env['foo'](0) == 0  # Exception caught, except block returns 0
