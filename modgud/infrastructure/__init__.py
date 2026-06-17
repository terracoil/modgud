"""Infrastructure layer - concrete guard runtime, registry, and AST transformer.

This is a pure container package and intentionally re-exports nothing. Import
each implementation from the leaf feature subpackage that owns it, e.g.
``from modgud.infrastructure.guarded_expr import GuardRuntime, CommonGuards`` or
``from modgud.infrastructure.implicit_ret import ImplicitReturnTransformer``.
"""
