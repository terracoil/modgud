"""Infrastructure layer - AST transformation and system boundaries."""

from .ast_transformer import DefaultAstTransformer, ImplicitReturnTransformer

__all__ = [
  'DefaultAstTransformer',
  'ImplicitReturnTransformer',  # Backward compatibility alias
]
