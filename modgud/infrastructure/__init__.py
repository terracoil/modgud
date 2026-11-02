"""Infrastructure layer - port adapters and shared infrastructure helpers.

This is a pure container package and intentionally re-exports nothing:

- ``modgud.infrastructure.adapters`` - ``GuardRuntime`` and ``ImplicitReturnTransformer``, the
  ``@Adapter`` implementations Idunn injects into the app decorators.
- ``modgud.infrastructure.common`` - ``CommonGuards`` and ``GuardRegistry`` (public), plus the
  AST helpers the transformer adapter uses.
"""
