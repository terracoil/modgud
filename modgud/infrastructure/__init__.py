"""Infrastructure layer for ``modgud``.

This package contains concrete implementations of domain ports. These
adapters handle technical concerns such as persistence, UUID
generation, and integration with external systems. The infrastructure
layer is allowed to depend on the domain layer (e.g., to import
port definitions), but it must never import from the presentation
layer.
"""

from .repository import InMemoryRepository
from .uuid_provider import UUIDProvider

__all__ = [
    "InMemoryRepository",
    "UUIDProvider",
]