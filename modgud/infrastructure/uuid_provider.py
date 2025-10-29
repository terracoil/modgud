"""Concrete UUID provider adapter.

This adapter implements the ``UUIDProviderPort`` using Python's
``uuid.uuid4`` to generate random UUIDs.
"""

import uuid

from modgud.domain.ports import UUIDProviderPort


class UUIDProvider(UUIDProviderPort):
    """Generate new UUID values using ``uuid4``."""

    def new_uuid(self) -> str:
        return uuid.uuid4().hex


__all__ = ["UUIDProvider"]