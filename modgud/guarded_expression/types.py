"""Type definitions for the guarded_expression module."""

from typing import Callable, Union

# Guard function signature: (*args, **kwargs) -> True | str
GuardFunction = Callable[..., Union[bool, str]]

# Failure behavior types
FailureTypes = Union[bool, str, int, float, None, dict, list, tuple]
FailureBehavior = Union[FailureTypes, Callable, type]
