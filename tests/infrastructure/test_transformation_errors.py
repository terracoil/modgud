"""Tests for error conditions during AST transformation."""

import pytest
from modgud.domain.models.errors import (
  ExplicitReturnDisallowedError,
  MissingImplicitReturnError,
)
from modgud.infrastructure.adapters.ast_transformer_adapter import AstTransformerAdapter


class TestTransformationErrors:
  """Tests for error conditions during AST transformation."""

  def test_explicit_return_raises_error(self):
    """Test that explicit return raises error."""
    source = """
def foo():
    return 10
"""
    with pytest.raises(ExplicitReturnDisallowedError):
      AstTransformerAdapter.apply_implicit_return_transform(source.strip(), 'foo')

  def test_if_without_else_raises_error(self):
    """Test that if without else at tail raises error."""
    source = """
def foo(x):
    if x > 0:
        "positive"
"""
    with pytest.raises(MissingImplicitReturnError):
      AstTransformerAdapter.apply_implicit_return_transform(source.strip(), 'foo')
