"""Inject decorator for dependency injection.

Re-exports from gleipnyr package.
"""

from gleipnyr import DependencyInjectionError, Inject, inject, inject_auto

__all__ = [
  'Inject',
  'inject',
  'inject_auto',
  'DependencyInjectionError',
]
