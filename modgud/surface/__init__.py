"""Presentation layer for ``modgud``.

The surface (or presentation) layer exposes the public API that end
users will call. It wires up the underlying domain services and
infrastructure adapters, providing a simple facade over the
architecture. None of the objects in this layer depend on concrete
infrastructure; they depend only on the domain and ports, and they
configure default adapters as needed.

Users can either call the high‑level functions defined here (such as
``create_entity``) or instantiate and use the lower layers directly
for more control.
"""

from __future__ import annotations

from threading import Lock
from typing import Optional

from modgud.domain.models import Entity
from modgud.domain.services import DomainService
from modgud.domain.ports import RepositoryPort, UUIDProviderPort
from modgud.infrastructure.repository import InMemoryRepository
from modgud.infrastructure.uuid_provider import UUIDProvider


_service_lock: Lock = Lock()
_default_service: Optional[DomainService] = None


def _get_default_service() -> DomainService:
    """Lazily create and return a default ``DomainService``.

    This function ensures that a single default service instance is
    created and reused. The service is configured with an in‑memory
    repository and a UUID provider.
    """

    global _default_service
    if _default_service is None:
        with _service_lock:
            if _default_service is None:
                repo = InMemoryRepository()
                uuid_provider = UUIDProvider()
                _default_service = DomainService(repository=repo, uuid_provider=uuid_provider)
    return _default_service


def create_entity(name: str, description: Optional[str] = None) -> Entity:
    """Create a new entity via the default service.

    If you need custom infrastructure, instantiate your own
    :class:`~modgud.domain.services.DomainService` instead of using this
    convenience function.
    """

    service = _get_default_service()
    return service.create_entity(name=name, description=description)


def get_entity(entity_id: str) -> Optional[Entity]:
    """Retrieve an entity by its ID via the default service."""

    service = _get_default_service()
    return service.get_entity(entity_id)


# Re‑export key symbols from lower layers so that consumers can
# configure their own service instances. Exposing these here avoids
# forcing users to reach deep into the package structure.
__all__ = [
    "create_entity",
    "get_entity",
    # Domain types
    "Entity",
    "DomainService",
    "RepositoryPort",
    "UUIDProviderPort",
    # Infrastructure adapters
    "InMemoryRepository",
    "UUIDProvider",
]