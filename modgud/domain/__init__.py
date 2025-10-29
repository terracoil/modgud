"""Domain layer for the ``modgud`` package.

The domain layer encapsulates the core business logic and models. It
defines the objects and operations that represent the problem space.
Nothing in this package depends on higher‑level layers such as
infrastructure or presentation. Instead, the domain declares
``ports``—abstract interfaces—which lower layers must implement.
"""

from . import models as models
from . import ports as ports
from .services import DomainService

__all__ = [
    "models",
    "ports",
    "DomainService",
]