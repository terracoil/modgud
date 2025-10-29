"""Type definitions for the guarded_expression module."""

from typing import Any, Callable

# Guard function signature: (*args, **kwargs) -> True | str
GuardFunction = Callable[..., bool | str]

# Failure behavior types
FailureTypes = bool | str | int | float | None | dict[str, Any] | list[Any] | tuple[Any, ...]
FailureBehavior = FailureTypes | Callable[..., Any] | type | Any
