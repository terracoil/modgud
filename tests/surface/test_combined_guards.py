"""Tests combining new guards with existing ones."""

import tempfile
from pathlib import Path

import pytest
from modgud import guarded_expression, matches_pattern, not_empty, valid_file_path, valid_url
from modgud.domain.models.errors import GuardClauseError


class TestCombinedGuards:
  """Tests combining new guards with existing ones."""

  def test_file_path_and_not_empty(self):
    """Test combining file path guard with not_empty."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as tmp:
      tmp_path = tmp.name
      tmp.write(b'content')

    try:

      @guarded_expression(
        valid_file_path('filepath', position=0, must_be_file=True),
        not_empty('content', position=1),
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
      valid_url('api_url'),
      matches_pattern(r'^https://api\..*', 'api_url'),
      implicit_return=False,
    )
    def call_api(api_url: str):
      return f'Calling {api_url}'

    result = call_api('https://api.example.com/endpoint')
    assert 'Calling' in result

    # Valid URL but wrong pattern
    with pytest.raises(GuardClauseError, match='must match pattern'):
      call_api('https://example.com/api')
