"""
API Tools - Development and utility tools for modgud.

This module provides development utilities, formatters, and analysis tools
that were migrated from the util/ layer. These tools are designed for
external programmatic access and provide higher-level functionality.

Components migrated from util/:
  - ansi_string: ANSI color formatting utilities
  - app_logger: Application logging configuration
  - console_formatter: Console output formatting
  - data_struct_util: Data structure manipulation utilities
  - dependency_analyzer: Package dependency analysis
  - json_formatter: JSON formatting utilities
  - output_capture: Output capture utilities for testing
  - ranger: Range and sequence utilities
  - spinner: CLI spinner functionality
  - text_util: Text processing and manipulation
  - version: Version utilities

These tools follow KLA principles:
- Dependencies flow downward only
- Pure functions where possible
- Clear separation of concerns
"""

# Import migrated utility components
from .ansi_string import AnsiString
from .app_logger import AppLogger, LoggerConfig
from .console_formatter import ConsoleFormatter
from .data_struct_util import DataStructUtil
from .dependency_analyzer import DependencyAnalyzer
from .json_formatter import JsonFormatter
from .output_capture import OutputCapture, OutputCaptureConfig, OutputFormatter
from .ranger import Ranger
from .spinner import CommandContext, ExecutionSpinner
from .text_util import TextUtil
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
  'OutputCapture',
  'OutputCaptureConfig',
  'OutputFormatter',
  'Ranger',
  'TextUtil',
  'get_project_version',
  'format_title_with_version',
]
