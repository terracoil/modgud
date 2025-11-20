"""Test helper utilities for modgud test suite."""

import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Optional

import pytest
from modgud.domain.exceptions import GuardClauseError


def assert_guard_fails(
  func: Callable, *args: Any, expected_message: Optional[str] = None, **kwargs: Any
) -> pytest.ExceptionInfo:
  """Assert that a guarded function fails with expected message."""
  with pytest.raises(GuardClauseError) as exc_info:
    func(*args, **kwargs)

  if expected_message:
    assert expected_message in str(exc_info.value)
  return exc_info


@contextmanager
def create_temp_file(content: str = 'test'):
  """Context manager for temporary test files."""
  with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
    tmp.write(content)
    tmp_path = tmp.name

  try:
    yield tmp_path
  finally:
    Path(tmp_path).unlink(missing_ok=True)
