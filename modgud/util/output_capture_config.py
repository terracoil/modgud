"""Output capture configuration for command execution."""

from dataclasses import dataclass

__all__ = ['OutputCaptureConfig']


@dataclass
class OutputCaptureConfig:
  """Configuration for output capture behavior."""

  enabled: bool = False
  capture_stdout: bool = True
  capture_stderr: bool = False
  capture_stdin: bool = False
  buffer_size: int = 1024 * 1024  # 1MB default
  encoding: str = 'utf-8'
  errors: str = 'replace'

  @classmethod
  def from_kwargs(cls, **kwargs) -> 'OutputCaptureConfig':
    """Create config from FreyjaCLI kwargs."""
    output_capture_config = kwargs.get('output_capture_config') or {}
    return cls(
      enabled=kwargs.get('capture_output', False),
      capture_stdout=kwargs.get('capture_stdout', True),
      capture_stderr=kwargs.get('capture_stderr', False),
      capture_stdin=kwargs.get('capture_stdin', False),
      **output_capture_config,
    )
