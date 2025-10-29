"""Domain models for the ``modgud`` package.

Domain models are simple data objects that capture the essential
attributes of entities in the problem space. They are defined using
Python's ``dataclasses`` for brevity and immutability. These models
are free from infrastructure concerns such as persistence or
serialization. Only the domain cares about these objects' invariants
and rules.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Entity:
    """A simple domain entity.

    An ``Entity`` has a unique identifier and a creation timestamp.
    Additional attributes can be added as your problem space demands.
    """

    id: str
    created_at: datetime
    name: str
    description: Optional[str] = None


__all__ = ["Entity"]