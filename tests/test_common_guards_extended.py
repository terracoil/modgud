"""Tests for extended CommonGuards validators (file_path, url, enum)."""

import tempfile
from enum import Enum
from pathlib import Path

import pytest
from modgud import CommonGuards, guarded_expression
from modgud.guarded_expression.errors import GuardClauseError


class TestValidFilePathGuard:
  """Tests for valid_file_path guard."""

  def test_valid_existing_file(self):
    """Test guard passes for existing file."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
      tmp_path = tmp.name

    try:

      @guarded_expression(
        CommonGuards.valid_file_path('filepath', must_be_file=True), implicit_return=False
      )
      def process_file(filepath: str):
        return f'Processing {filepath}'

      result = process_file(tmp_path)
      assert 'Processing' in result
    finally:
      Path(tmp_path).unlink()

  def test_nonexistent_file_fails(self):
    """Test guard fails for nonexistent file."""

    @guarded_expression(CommonGuards.valid_file_path('filepath'), implicit_return=False)
    def process_file(filepath: str):
      return f'Processing {filepath}'

    with pytest.raises(GuardClauseError, match='does not exist'):
      process_file('/nonexistent/path/to/file.txt')

  def test_valid_directory(self):
    """Test guard passes for existing directory."""
    with tempfile.TemporaryDirectory() as tmp_dir:

      @guarded_expression(
        CommonGuards.valid_file_path('dirpath', must_be_dir=True), implicit_return=False
      )
      def process_dir(dirpath: str):
        return f'Processing {dirpath}'

      result = process_dir(tmp_dir)
      assert 'Processing' in result

  def test_file_when_directory_required_fails(self):
    """Test guard fails when file provided but directory required."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
      tmp_path = tmp.name

    try:

      @guarded_expression(
        CommonGuards.valid_file_path('dirpath', must_be_dir=True), implicit_return=False
      )
      def process_dir(dirpath: str):
        return f'Processing {dirpath}'

      with pytest.raises(GuardClauseError, match='must be a directory'):
        process_dir(tmp_path)
    finally:
      Path(tmp_path).unlink()

  def test_allow_nonexistent_path(self):
    """Test guard passes for nonexistent path when must_exist=False."""

    @guarded_expression(
      CommonGuards.valid_file_path('filepath', must_exist=False), implicit_return=False
    )
    def create_file(filepath: str):
      return f'Creating {filepath}'

    result = create_file('/path/to/new/file.txt')
    assert 'Creating' in result


class TestValidUrlGuard:
  """Tests for valid_url guard."""

  def test_valid_http_url(self):
    """Test guard passes for valid HTTP URL."""

    @guarded_expression(CommonGuards.valid_url('url'), implicit_return=False)
    def fetch_url(url: str):
      return f'Fetching {url}'

    result = fetch_url('http://example.com')
    assert 'Fetching' in result

  def test_valid_https_url(self):
    """Test guard passes for valid HTTPS URL."""

    @guarded_expression(CommonGuards.valid_url('url'), implicit_return=False)
    def fetch_url(url: str):
      return f'Fetching {url}'

    result = fetch_url('https://example.com/path?query=value')
    assert 'Fetching' in result

  def test_url_without_scheme_fails(self):
    """Test guard fails for URL without scheme when require_scheme=True."""

    @guarded_expression(CommonGuards.valid_url('url', require_scheme=True), implicit_return=False)
    def fetch_url(url: str):
      return f'Fetching {url}'

    with pytest.raises(GuardClauseError, match='must include a scheme'):
      fetch_url('example.com')

  def test_url_without_scheme_allowed(self):
    """Test guard passes for URL without scheme when require_scheme=False."""

    @guarded_expression(CommonGuards.valid_url('url', require_scheme=False), implicit_return=False)
    def fetch_url(url: str):
      return f'Fetching {url}'

    result = fetch_url('example.com/path')
    assert 'Fetching' in result

  def test_invalid_url_fails(self):
    """Test guard fails for completely invalid URL."""

    @guarded_expression(CommonGuards.valid_url('url'), implicit_return=False)
    def fetch_url(url: str):
      return f'Fetching {url}'

    with pytest.raises(GuardClauseError, match='must include a scheme'):
      fetch_url('   ')


class TestValidEnumGuard:
  """Tests for valid_enum guard."""

  def test_valid_enum_value(self):
    """Test guard passes for valid enum value."""

    class Color(Enum):
      RED = 'red'
      GREEN = 'green'
      BLUE = 'blue'

    @guarded_expression(CommonGuards.valid_enum(Color, 'color'), implicit_return=False)
    def set_color(color: str):
      return f'Color set to {color}'

    result = set_color('red')
    assert 'Color set to' in result

  def test_enum_instance_passes(self):
    """Test guard passes when enum instance provided."""

    class Status(Enum):
      ACTIVE = 'active'
      INACTIVE = 'inactive'

    @guarded_expression(CommonGuards.valid_enum(Status, 'status'), implicit_return=False)
    def set_status(status):
      return f'Status: {status.value if isinstance(status, Status) else status}'

    result = set_status(Status.ACTIVE)
    assert 'active' in result

  def test_invalid_enum_value_fails(self):
    """Test guard fails for invalid enum value."""

    class Priority(Enum):
      LOW = 'low'
      MEDIUM = 'medium'
      HIGH = 'high'

    @guarded_expression(CommonGuards.valid_enum(Priority, 'priority'), implicit_return=False)
    def set_priority(priority: str):
      return f'Priority: {priority}'

    with pytest.raises(GuardClauseError, match='must be one of'):
      set_priority('urgent')

  def test_none_value_fails(self):
    """Test guard fails when None provided."""

    class Mode(Enum):
      DEBUG = 'debug'
      RELEASE = 'release'

    @guarded_expression(CommonGuards.valid_enum(Mode, 'mode'), implicit_return=False)
    def set_mode(mode: str):
      return f'Mode: {mode}'

    with pytest.raises(GuardClauseError, match='is required'):
      set_mode(None)


class TestCombinedGuards:
  """Tests combining new guards with existing ones."""

  def test_file_path_and_not_empty(self):
    """Test combining file path guard with not_empty."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as tmp:
      tmp_path = tmp.name
      tmp.write(b'content')

    try:

      @guarded_expression(
        CommonGuards.valid_file_path('filepath', position=0, must_be_file=True),
        CommonGuards.not_empty('content', position=1),
        implicit_return=False,
      )
      def process_file_with_content(filepath: str, content: str):
        return {'file': filepath, 'content': content}

      result = process_file_with_content(tmp_path, 'some content')
      assert result['content'] == 'some content'

      # Empty content should fail
      with pytest.raises(GuardClauseError, match='content cannot be empty'):
        process_file_with_content(tmp_path, '')
    finally:
      Path(tmp_path).unlink()

  def test_url_and_pattern_match(self):
    """Test combining URL guard with pattern matching."""

    @guarded_expression(
      CommonGuards.valid_url('api_url'),
      CommonGuards.matches_pattern(r'^https://api\..*', 'api_url'),
      implicit_return=False,
    )
    def call_api(api_url: str):
      return f'Calling {api_url}'

    result = call_api('https://api.example.com/endpoint')
    assert 'Calling' in result

    # Valid URL but wrong pattern
    with pytest.raises(GuardClauseError, match='must match pattern'):
      call_api('https://example.com/api')
