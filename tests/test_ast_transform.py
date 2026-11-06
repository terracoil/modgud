"""Unit tests for AST transformation logic."""

import ast

import pytest
from modgud import ExplicitReturnDisallowedError, MissingImplicitReturnError
from modgud.infrastructure.adapters import ImplicitReturnAdapter


class TestBasicTransformations:
  """Tests for basic AST transformations of common patterns."""

  def test_simple_expression_transform(self):
    """Test transformation of simple expression."""
    source = """
def foo():
    x = 10
    x + 5
"""
    tree, filename = ImplicitReturnAdapter.apply_implicit_return_transform(source.strip(), 'foo')
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
    tree, _ = ImplicitReturnAdapter.apply_implicit_return_transform(source.strip(), 'foo')
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
    tree, _ = ImplicitReturnAdapter.apply_implicit_return_transform(source.strip(), 'foo')
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
      ImplicitReturnAdapter.apply_implicit_return_transform(source.strip(), 'foo')

  def test_if_without_else_raises_error(self):
    """Test that if without else at tail raises error."""
    source = """
def foo(x):
    if x > 0:
        "positive"
"""
    with pytest.raises(MissingImplicitReturnError):
      ImplicitReturnAdapter.apply_implicit_return_transform(source.strip(), 'foo')


class TestEdgeCases:
  """Tests for edge cases and special scenarios in AST transformation."""

  def test_empty_block_returns_none(self):
    """Test that function with only pass returns None gracefully."""
    source = """
def foo():
    pass
"""
    tree, _ = ImplicitReturnAdapter.apply_implicit_return_transform(source.strip(), 'foo')
    # Should transform successfully and return None
    assert isinstance(tree, ast.Module)

  def test_nested_function_return_refused(self):
    """A ``return`` inside a nested def is refused too, with the nested return's position."""
    source = """
def outer():
    def inner():
        return 10
    x = inner()
    x + 5
"""
    with pytest.raises(ExplicitReturnDisallowedError) as exc_info:
      ImplicitReturnAdapter.apply_implicit_return_transform(source.strip(), 'outer')
    assert (exc_info.value.lineno, exc_info.value.offset) == (3, 8)

  def test_nested_async_def_and_method_returns_refused(self):
    """Nested coroutines and methods of nested classes are part of the body as well."""
    async_source = """
def outer():
    async def inner():
        return 10
    inner
"""
    class_source = """
def outer():
    class Inner:
        def value(self):
            return 10
    Inner
"""
    for source in (async_source, class_source):
      with pytest.raises(ExplicitReturnDisallowedError):
        ImplicitReturnAdapter.apply_implicit_return_transform(source.strip(), 'outer')

  def test_first_return_is_reported(self):
    """With several returns, the error points at the first one in source order."""
    source = """
def outer(x):
    def inner():
        return 1
    return inner
"""
    with pytest.raises(ExplicitReturnDisallowedError) as exc_info:
      ImplicitReturnAdapter.apply_implicit_return_transform(source.strip(), 'outer')
    assert exc_info.value.lineno == 3

  def test_nested_lambda_not_transformed(self):
    """Test nested lambda functions are not transformed."""
    source = """
def foo(x):
    f = lambda y: y + 1
    result = f(x)
    result * 2
"""
    tree, _ = ImplicitReturnAdapter.apply_implicit_return_transform(source.strip(), 'foo')
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
    tree, _ = ImplicitReturnAdapter.apply_implicit_return_transform(source.strip(), 'foo')
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
        case _:
            "other"
"""
    tree, _ = ImplicitReturnAdapter.apply_implicit_return_transform(source.strip(), 'foo')
    code = compile(tree, '<test>', 'exec')
    env = {}
    exec(code, env)
    assert env['foo'](1) is None
    assert env['foo'](2) == 'other'

  @pytest.mark.parametrize(
    'last_case',
    ['case 2:', 'case _ if x > 2:', 'case other if other > 2:', 'case [_, *_]:'],
  )
  def test_match_without_wildcard_refused(self, last_case):
    """A tail match whose last case can fail would leave the result unset; refuse it early."""
    source = f"""
def foo(x):
    match x:
        case 1:
            "one"
        {last_case}
            "two"
"""
    with pytest.raises(MissingImplicitReturnError, match='must end in a wildcard case') as exc_info:
      ImplicitReturnAdapter.apply_implicit_return_transform(source.strip(), 'foo')
    assert exc_info.value.lineno == 2

  def test_nested_tail_match_without_wildcard_refused(self):
    """The rule applies to a match in any tail position, not only the function's last line."""
    source = """
def foo(x, flag):
    if flag:
        match x:
            case 1:
                "one"
    else:
        "flag off"
"""
    with pytest.raises(MissingImplicitReturnError, match='must end in a wildcard case'):
      ImplicitReturnAdapter.apply_implicit_return_transform(source.strip(), 'foo')

  def test_match_not_at_tail_needs_no_wildcard(self):
    """A match earlier in the body is ordinary code; only tail positions must yield a value."""
    source = """
def foo(x):
    label = "other"
    match x:
        case 1:
            label = "one"
    label
"""
    tree, _ = ImplicitReturnAdapter.apply_implicit_return_transform(source.strip(), 'foo')
    code = compile(tree, '<test>', 'exec')
    env = {}
    exec(code, env)
    assert env['foo'](1) == 'one'
    assert env['foo'](5) == 'other'

  @pytest.mark.parametrize(
    ('last_case', 'expected'),
    [
      ('case _:', 'fallback'),
      ('case other:', 'fallback 5'),
      ('case 2 | _:', 'fallback'),
      ('case (other as alias):', 'fallback 5'),
    ],
  )
  def test_match_with_irrefutable_last_case_accepted(self, last_case, expected):
    """``case _:``, a bare capture, or an or/as pattern around one all close the match."""
    body = "f'fallback {other}'" if 'other' in last_case else "'fallback'"
    source = f"""
def foo(x):
    match x:
        case 1:
            "one"
        {last_case}
            {body}
"""
    tree, _ = ImplicitReturnAdapter.apply_implicit_return_transform(source.strip(), 'foo')
    code = compile(tree, '<test>', 'exec')
    env = {}
    exec(code, env)
    assert env['foo'](1) == 'one'
    assert env['foo'](5) == expected

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
    tree, _ = ImplicitReturnAdapter.apply_implicit_return_transform(source.strip(), 'foo')
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
    tree, _ = ImplicitReturnAdapter.apply_implicit_return_transform(source.strip(), 'foo')
    assert isinstance(tree, ast.Module)
    # Verify it compiles and works
    code = compile(tree, '<test>', 'exec')
    env = {}
    exec(code, env)
    assert env['foo'](2) == 3  # No exception, try succeeds (10/2=5), else runs (2+1=3)
    assert env['foo'](0) == 0  # Exception caught, except block returns 0
