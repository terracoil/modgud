"""Domain layer - passive types, enums, errors, and ports.

This is a pure container package and intentionally re-exports nothing. Import
each symbol from the leaf feature subpackage that owns it, e.g.
``from modgud.domain.guarded_expr import GuardFailurEnum`` or
``from modgud.domain.implicit_ret import ImplicitReturnError``.
"""
