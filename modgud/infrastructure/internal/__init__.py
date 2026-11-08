"""Helpers shared by the adapters; internal to the infrastructure layer.

Only ``modgud.infrastructure.adapters`` imports this package, and nothing re-exports it further.
"""

from .method_descriptors import MethodDescriptors

__all__ = ['MethodDescriptors']
