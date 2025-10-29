"""Concrete repository adapter.

This adapter provides an in‑memory implementation of the
``RepositoryPort`` defined in :mod:`modgud.domain.ports`. It can be
replaced with a database-backed implementation without changing the
domain or presentation layers.
"""

from __future__ import annotations

from threading import Lock
from typing import Dict, Optional

from modgud.domain.models import Entity
from modgud.domain.ports import RepositoryPort


class InMemoryRepository(RepositoryPort):
    """A thread‑safe in‑memory repository for ``Entity`` objects."""

    def __init__(self) -> None:
        self._entities: Dict[str, Entity] = {}
        self._lock = Lock()

    def save(self, entity: Entity) -> None:
        with self._lock:
            self._entities[entity.id] = entity

    def get(self, entity_id: str) -> Optional[Entity]:
        with self._lock:
            return self._entities.get(entity_id)


__all__ = ["InMemoryRepository"]