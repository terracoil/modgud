"""Command context for execution display."""

from dataclasses import dataclass, field
from typing import Any

__all__ = ['CommandContext']


@dataclass
class CommandContext:
  """Context for command execution display."""

  namespace: str | None = None
  command: str = ''
  subcommand: str | None = None
  global_args: dict[str, Any] = field(default_factory=dict)
  group_args: dict[str, Any] = field(default_factory=dict)
  command_args: dict[str, Any] = field(default_factory=dict)
  positional_args: list[Any] = field(default_factory=list)
  custom_status: str | None = None