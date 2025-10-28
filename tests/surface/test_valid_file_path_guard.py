"""Tests for valid_file_path guard."""

import tempfile
from pathlib import Path

import pytest
from modgud import guarded_expression, valid_file_path
from modgud.domain.models.errors import GuardClauseError

from tests.helpers import create_temp_file


class TestValidFilePathGuard:
  """Tests for valid_file_path guard."""

  def test_valid_existing_file(self):
    """Test guard passes for existing file."""
    with create_temp_file('test content') as tmp_path:

      @guarded_expression(valid_file_path('filepath', must_be_file=True), implicit_return=False)
      def process_file(filepath: str):
        return f'Processing {filepath}'

      result = process_file(tmp_path)
      assert 'Processing' in result

  def test_nonexistent_file_fails(self):
    """Test guard fails for nonexistent file."""

    @guarded_expression(valid_file_path('filepath'), implicit_return=False)
    def process_file(filepath: str):
      return f'Processing {filepath}'

    with pytest.raises(GuardClauseError, match='does not exist'):
      process_file('/nonexistent/path/to/file.txt')

  def test_valid_directory(self):
    """Test guard passes for existing directory."""
    with tempfile.TemporaryDirectory() as tmp_dir:

      @guarded_expression(valid_file_path('dirpath', must_be_dir=True), implicit_return=False)
      def process_dir(dirpath: str):
        return f'Processing {dirpath}'

      result = process_dir(tmp_dir)
      assert 'Processing' in result

  def test_file_when_directory_required_fails(self):
    """Test guard fails when file provided but directory required."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
      tmp_path = tmp.name

    try:

      @guarded_expression(valid_file_path('dirpath', must_be_dir=True), implicit_return=False)
      def process_dir(dirpath: str):
        return f'Processing {dirpath}'

      with pytest.raises(GuardClauseError, match='must be a directory'):
        process_dir(tmp_path)
    finally:
      Path(tmp_path).unlink()

  def test_allow_nonexistent_path(self):
    """Test guard passes for nonexistent path when must_exist=False."""

    @guarded_expression(valid_file_path('filepath', must_exist=False), implicit_return=False)
    def create_file(filepath: str):
      return f'Creating {filepath}'

    result = create_file('/path/to/new/file.txt')
    assert 'Creating' in result
