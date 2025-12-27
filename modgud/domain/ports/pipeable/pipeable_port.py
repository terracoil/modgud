"""Port definition for objects that support pipeline operations via | operator."""

from __future__ import annotations

from typing import Any, Protocol, Union, runtime_checkable


@runtime_checkable
class PipeablePort(Protocol):
  """
  Port for objects that support pipeline operations via | operator.

  This port defines the interface for pipeable objects that enable
  functional-style pipeline composition with partial application support.
  """

  def __or__(self, other: Union['PipeablePort', Any]) -> Any:
    """
    Enable func | func syntax for pipeline operations.

    Args:
        other: The next function in the pipeline

    Returns:
        Result of pipeline operation

    """
    ...

  def __ror__(self, other: Any) -> Any:
    """
    Enable value | func syntax (reverse or).

    This is the main entry point for pipeline operations starting with a value.

    Args:
        other: The value to pipe into this function

    Returns:
        The result of applying the function to the value

    """
    ...

  def __call__(self, *args: Any, **kwargs: Any) -> Union['PipeablePort', Any]:
    """
    Execute the wrapped function or create a partial application.

    This method tries to execute the function with the provided arguments.
    If execution fails due to missing required arguments, it returns a
    partial application with bound arguments.

    Args:
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function

    Returns:
        Either a new Pipeable with bound arguments or the function result

    """
    ...

  def __repr__(self) -> str:
    """Return a string representation of the Pipeable."""
    ...
