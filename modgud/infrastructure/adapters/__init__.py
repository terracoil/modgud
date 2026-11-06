"""Idunn adapters: the concrete implementations of modgud's ports.

Idunn discovers these the first time an app decorator needs a port, through
``@Invert(bootstrap='modgud')``, and injects them. Nothing outside this package and its unit
tests imports them.
"""

from .guard_adapter import GuardAdapter
from .implicit_return_adapter import ImplicitReturnAdapter

__all__ = [
  'GuardAdapter',
  'ImplicitReturnAdapter',
]
