"""
API layer - Public-facing utilities and tools.

This layer contains utilities and tools that provide programmatic access to
modgud functionality. These are intended for external consumption and provide
higher-level abstractions over the core infrastructure.

Following KLA (Kinetic Layer Architecture) principles:
- Dependencies flow downward: api -> infrastructure/domain/util
- No upward dependencies allowed
- Pure functions and immutable objects where possible

Primary modules:
  - tools: Development and analysis utilities
"""

# Re-export commonly used tools
from .tools import (
  AnsiString,
  AppLogger,
  CommandContext,
  ConsoleFormatter,
  DataStructUtil,
  DependencyAnalyzer,
  ExecutionSpinner,
  JsonFormatter,
  LoggerConfig,
  OutputCapture,
  OutputCaptureConfig,
  OutputFormatter,
  Ranger,
  TextUtil,
  format_title_with_version,
  get_project_version,
)

__all__ = [
  # Re-exported from tools
  'AnsiString',
  'AppLogger',
  'LoggerConfig',
  'CommandContext',
  'ConsoleFormatter',
  'DataStructUtil',
  'DependencyAnalyzer',
  'ExecutionSpinner',
  'JsonFormatter',
  'OutputCapture',
  'OutputCaptureConfig',
  'OutputFormatter',
  'Ranger',
  'TextUtil',
  'get_project_version',
  'format_title_with_version',
]
