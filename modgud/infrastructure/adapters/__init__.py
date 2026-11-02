"""Idunn adapters: the concrete implementations of modgud's ports.

Idunn discovers these through ``Idunn().bootstrap('modgud')`` and injects them into the app
decorators via ``@Invert``. Nothing outside this package and its unit tests imports them.
"""

from .guard_runtime import GuardRuntime
from .implicit_return_transformer import ImplicitReturnTransformer

__all__ = [
  'GuardRuntime',
  'ImplicitReturnTransformer',
]
