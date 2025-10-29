"""Domain services orchestrating business use cases.

Domain services provide methods that coordinate interactions between
models and ports. They encapsulate business rules and workflows. By
relying solely on ports, services are decoupled from concrete
infrastructure implementations.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from typing import Optional

from .models import Entity
from .ports import RepositoryPort, UUIDProviderPort


class DomainService:
    """A service providing simple CRUD operations for ``Entity`` objects."""

    def __init__(
        self,
        repository: RepositoryPort,
        uuid_provider: UUIDProviderPort,
    ) -> None:
        self._repository = repository
        self._uuid_provider = uuid_provider

    def create_entity(self, name: str, description: Optional[str] = None) -> Entity:
        """Create and persist a new entity.

        A unique identifier is generated via the ``UUIDProviderPort`` and
        assigned to the new entity. The entity is then persisted via the
        ``RepositoryPort``.
        """

        entity_id = self._uuid_provider.new_uuid()
        entity = Entity(id=entity_id, created_at=datetime.utcnow(), name=name, description=description)
        self._repository.save(entity)
        return entity

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Retrieve an entity by its identifier."""

        return self._repository.get(entity_id)

    def update_entity_name(self, entity_id: str, new_name: str) -> Optional[Entity]:
        """Update the name of an existing entity and persist the changes.

        Returns the updated entity, or ``None`` if the entity does not exist.
        """

        entity = self._repository.get(entity_id)
        if entity is None:
            return None
        updated = replace(entity, name=new_name)
        self._repository.save(updated)
        return updated


__all__ = ["DomainService"]