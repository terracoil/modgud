"""Type definitions for the modgud library.

The domain layer is passive and contains no business logic - only type
definitions and protocols used across the library.
"""

from typing import Any, Callable, TypeVar

GuardFunction = Callable[..., bool | str]
T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])  # a decorated callable, handed back as the same type
