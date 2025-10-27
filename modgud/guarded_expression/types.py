"""Type definitions for the guarded_expression module."""

from typing import Any, Callable, Union

# Guard function signature: (*args, **kwargs) -> True | str
GuardFunction = Callable[..., Union[bool, str]]

# Failure behavior types
FailureTypes = Union[bool, str, int, float, None, dict[str, Any], list[Any], tuple[Any, ...]]
FailureBehavior = Union[FailureTypes, Callable[..., Any], type]
