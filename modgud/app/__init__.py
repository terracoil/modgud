"""Application layer: the two public decorators."""

from .guarded_expression import guarded_expression
from .implicit_return import implicit_return

__all__ = [
  'guarded_expression',
  'implicit_return',
]

# from idunn import Idunn

# print("Running autodiscover...")
# Idunn().autodiscover('modgud')   # idempotent; survives a prior reset()
