"""
Utility module - Generic utilities for modgud.

This module provides generic utility functions and classes:
- Math utilities
- ANSI string formatting
- Application logging
- Console formatting
- Data structure utilities
- Dependency analysis
- JSON formatting
- Output capture
- CLI spinner
- Version utilities
"""

from .ansi_string import AnsiString
from .console_formatter import ConsoleFormatter
from .data_struct_util import DataStructUtil
from .dependency_analyzer import DependencyAnalyzer
from .json_formatter import JsonFormatter
from .logging import AppLogger, LoggerConfig
from .math_util import MathUtil
from .output_capture import OutputCapture, OutputCaptureConfig, OutputFormatter
from .spinner import CommandContext, ExecutionSpinner
from .version import format_title_with_version, get_project_version

__all__ = [
  'AnsiString',
  'AppLogger',
  'LoggerConfig',
  'CommandContext',
  'ConsoleFormatter',
  'DataStructUtil',
  'DependencyAnalyzer',
  'ExecutionSpinner',
  'JsonFormatter',
  'MathUtil',
  'OutputCapture',
  'OutputCaptureConfig',
  'OutputFormatter',
  'format_title_with_version',
  'get_project_version',
]
