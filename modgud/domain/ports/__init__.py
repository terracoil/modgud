"""
Domain layer ports - contracts for infrastructure implementations.

These ports define the contracts that infrastructure layer adapters must implement.
Following the Dependency Inversion Principle, the domain (inner layer) defines
what it needs, and infrastructure (outer layer) provides implementations.
"""

from .ast_transformer_port import AstTransformerPort
from .guard_checker_port import GuardCheckerPort

__all__ = [
  'GuardCheckerPort',
  'AstTransformerPort',
]
