"""Top-level package for the ``modgud`` library.

This package implements the Layered Ports Architecture (LPA) in a
canonical form. All public APIs intended for end users live in the
``surface`` subpackage. Higher‑level layers are permitted to depend
inward on any lower layer through ports (interfaces), but never
outward. See :mod:`modgud.domain` for domain logic, and
``modgud.infrastructure`` for concrete implementations of ports.

The top‑level ``modgud`` namespace re‑exports selected names from
``modgud.surface`` so that users can import them directly from
``modgud`` without digging into the package structure. Only items
defined in ``surface`` are exported here; internal types and
implementations remain encapsulated.
"""

# Expose the entire public API defined in :mod:`modgud.surface`.
from .surface import (
    create_entity,
    get_entity,
    Entity,
    DomainService,
    RepositoryPort,
    UUIDProviderPort,
    InMemoryRepository,
    UUIDProvider,
)

__all__ = [
    "create_entity",
    "get_entity",
    "Entity",
    "DomainService",
    "RepositoryPort",
    "UUIDProviderPort",
    "InMemoryRepository",
    "UUIDProvider",
]