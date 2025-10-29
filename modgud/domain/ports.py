"""Abstract ports for the ``modgud`` domain.

Ports are abstract interfaces that declare the operations the domain
requires from lower layers. Concrete implementations of these ports
live in the :mod:`modgud.infrastructure` package. The domain never
imports such implementations directly; instead, they are passed in
through dependency injection.

For example, the domain defines a ``RepositoryPort`` that a
persistence adapter must implement to save and load entities. A
``UUIDProviderPort`` supplies unique identifiers for new entities.
"""

from __future__ import annotations

import abc
from typing import Protocol, runtime_checkable, Optional

from .models import Entity


@runtime_checkable
class RepositoryPort(Protocol):
    """A port for persisting and retrieving domain entities.

    Concrete infrastructure adapters (e.g., SQL or in-memory
    repositories) must implement this protocol.
    """

    def save(self, entity: Entity) -> None:
        """Persist a new or updated entity."""

        raise NotImplementedError

    def get(self, entity_id: str) -> Optional[Entity]:
        """Retrieve an entity by its unique identifier.

        Returns ``None`` if the entity does not exist.
        """

        raise NotImplementedError


@runtime_checkable
class UUIDProviderPort(Protocol):
    """A port that generates unique identifiers for entities."""

    def new_uuid(self) -> str:
        """Return a new unique identifier."""

        raise NotImplementedError


__all__ = ["RepositoryPort", "UUIDProviderPort"]