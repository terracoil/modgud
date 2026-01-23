"""Output capture utilities for command execution."""

import sys
from contextlib import contextmanager
from io import StringIO

__all__ = ['OutputCapture']


class OutputCapture:
  """Captures stdout and stderr during command execution."""

  def __init__(
    self,
    capture_stdout: bool = True,
    capture_stderr: bool = False,
    capture_stdin: bool = False,
    buffer_size: int = 1024 * 1024,
    encoding: str = 'utf-8',
    errors: str = 'replace',
  ):
    """Initialize output capture with configurable streams.

    :param capture_stdout: Whether to capture stdout
    :param capture_stderr: Whether to capture stderr
    :param capture_stdin: Whether to capture stdin
    :param buffer_size: Buffer size for captured streams
    :param encoding: Text encoding for buffers
    :param errors: Error handling for encoding
    """
    self.capture_stdout = capture_stdout
    self.capture_stderr = capture_stderr
    self.capture_stdin = capture_stdin
    self.buffer_size = buffer_size
    self.encoding = encoding
    self.errors = errors

    # Create buffers only for streams we're capturing
    self.stdout_buffer = StringIO() if capture_stdout else None
    self.stderr_buffer = StringIO() if capture_stderr else None
    self.stdin_buffer = StringIO() if capture_stdin else None

    # Original streams
    self.original_stdout: object | None = None
    self.original_stderr: object | None = None
    self.original_stdin: object | None = None
    self._active = False

  def start(self):
    """Start capturing output.

    :raises RuntimeError: If capture is already active
    """
    if self._active:
      raise RuntimeError('Output capture is already active')

    # Store original streams and replace with buffers if capturing
    if self.capture_stdout:
      self.original_stdout = sys.stdout
      sys.stdout = self.stdout_buffer

    if self.capture_stderr:
      self.original_stderr = sys.stderr
      sys.stderr = self.stderr_buffer

    if self.capture_stdin:
      self.original_stdin = sys.stdin
      sys.stdin = self.stdin_buffer

    self._active = True

  def stop(self) -> tuple[str, str]:
    """Stop capturing and return captured output.

    :return: Tuple of (stdout_content, stderr_content)
    :raises RuntimeError: If capture is not active
    """
    if not self._active:
      raise RuntimeError('Output capture is not active')

    # Get captured content before restoring streams
    stdout_content = self.stdout_buffer.getvalue() if self.stdout_buffer else ''
    stderr_content = self.stderr_buffer.getvalue() if self.stderr_buffer else ''

    # Restore original streams
    if self.original_stdout:
      sys.stdout = self.original_stdout
    if self.original_stderr:
      sys.stderr = self.original_stderr
    if self.original_stdin:
      sys.stdin = self.original_stdin

    self._active = False
    self.original_stdout = None
    self.original_stderr = None
    self.original_stdin = None

    # Note: We DON'T reset buffers here so captured content remains available
    # Users can call clear() if they want to reset

    return stdout_content, stderr_content

  def is_active(self) -> bool:
    """Check if capture is currently active.

    :return: True if capture is active
    """
    return self._active

  @contextmanager
  def capture_output(self):
    """Context manager for output capture.

    Usage:
        capture = OutputCapture()
        with capture.capture_output():
            print("This will be captured")
        stdout, stderr = capture.stop()
    """
    self.start()
    try:
      yield self
    finally:
      if self._active:  # Only stop if still active
        self.stop()

  def get_output(self, stream: str = 'stdout') -> str | None:
    """Get captured output for specific stream.

    :param stream: Stream name ('stdout', 'stderr', 'stdin')
    :return: Captured content or None if stream not captured
    """
    buffer_map = {
      'stdout': self.stdout_buffer,
      'stderr': self.stderr_buffer,
      'stdin': self.stdin_buffer,
    }
    buffer = buffer_map.get(stream)
    if buffer:
      return buffer.getvalue()
    return None

  def get_all_output(self) -> dict[str, str | None]:
    """Get all captured output.

    :return: Dictionary with captured content for each stream
    """
    return {
      'stdout': self.get_output('stdout'),
      'stderr': self.get_output('stderr'),
      'stdin': self.get_output('stdin'),
    }

  def clear(self) -> None:
    """Clear all capture buffers."""
    if self.stdout_buffer:
      self.stdout_buffer.seek(0)
      self.stdout_buffer.truncate(0)
    if self.stderr_buffer:
      self.stderr_buffer.seek(0)
      self.stderr_buffer.truncate(0)
    if self.stdin_buffer:
      self.stdin_buffer.seek(0)
      self.stdin_buffer.truncate(0)
