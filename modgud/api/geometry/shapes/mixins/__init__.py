"""
Mixins for shape decoration and validation.

These mixins provide composable capabilities that can be mixed into shape classes:
- ValidationMixin: Parameter validation
- TornEdgesMixin: Noise-based edge distortion
- NotchesMixin: Rectangular indentations with angle awareness
"""

from .notches import NotchesMixin
from .torn_edges import TornEdgesMixin
from .validation import ValidationMixin

__all__ = [
  'ValidationMixin',
  'TornEdgesMixin',
  'NotchesMixin',
]
