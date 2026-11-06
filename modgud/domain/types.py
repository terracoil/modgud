"""Domain type definitions for modgud.

The domain layer is passive and contains no business logic - only type
definitions and protocols used across the library.
"""

from typing import Callable

GuardFunction = Callable[..., bool | str]
