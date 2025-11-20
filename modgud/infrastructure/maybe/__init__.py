"""
Maybe monad types for optional values.

This sub-package contains the Maybe monad implementation with
Some and Nothing types for null-safe programming patterns.
"""

from ...domain.maybe_protocol import MaybeProtocol as Maybe
from .nothing_maybe import Nothing
from .some_maybe import Some

__all__ = [
  'Maybe',
  'Some',
  'Nothing',
]
