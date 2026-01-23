"""Output formatting utilities for captured command output."""

import sys

__all__ = ['OutputFormatter']


class OutputFormatter:
  """Formats captured output with command prefixes."""

  def __init__(self, color_formatter=None):
    """Initialize output formatter.

    :param color_formatter: ColorFormatter instance for styling
    """
    self.color_formatter = color_formatter

  def format_output(
    self, command_name: str, stdout: str, stderr: str, style_name: str = 'command_output'
  ) -> None:
    """Format and print captured output with command prefix.

    :param command_name: Name of the command that generated the output
    :param stdout: Captured stdout content
    :param stderr: Captured stderr content
    :param style_name: Name of the style to apply to prefixes
    """
    prefix = f'{{{command_name}}}'

    # Apply styling to prefix if color formatter is available
    if self.color_formatter and hasattr(self.color_formatter, 'apply_style'):
      try:
        # TODO: Theme support removed during migration to api/tools
        # from ..theme.defaults import create_default_theme
        # theme = create_default_theme()
        # styled_prefix = self.color_formatter.apply_style(
        #   prefix, getattr(theme, style_name, theme.command_output)
        # )
        styled_prefix = prefix
      except Exception:
        # Fall back to plain prefix if styling fails
        styled_prefix = prefix
    else:
      styled_prefix = prefix

    # Display stdout with prefix
    if stdout:
      for line in stdout.splitlines():
        if line.strip():  # Skip empty lines
          print(f'{styled_prefix} {line}')

    # Display stderr with prefix and error marker
    if stderr:
      error_prefix = f'{styled_prefix} [ERROR]'
      for line in stderr.splitlines():
        if line.strip():  # Skip empty lines
          print(error_prefix + f' {line}', file=sys.stderr)

  def should_display_output(self, verbose: bool, command_success: bool) -> bool:
    """Determine if output should be displayed.

    :param verbose: Whether verbose mode is enabled
    :param command_success: Whether the command succeeded
    :return: True if output should be displayed
    """
    # ALWAYS show command output - users expect to see the results of their commands
    # This was the core issue: output was being hidden except in verbose mode or on failure
    return True
