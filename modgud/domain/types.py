"""Domain type definitions for modgud.

The domain layer is passive and contains no business logic - only type
definitions and protocols used across the library.
"""

from typing import Callable

__all__ = ['GuardFunction']

# Guard function signature: (*args, **kwargs) -> True | str
# Guards return True for success, or an error message string for failure.
GuardFunction = Callable[..., bool | str]
