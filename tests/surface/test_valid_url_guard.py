"""Tests for valid_url guard."""

import pytest
from modgud import guarded_expression, valid_url
from modgud.domain.models.errors import GuardClauseError


class TestValidUrlGuard:
  """Tests for valid_url guard."""

  def test_valid_http_url(self):
    """Test guard passes for valid HTTP URL."""

    @guarded_expression(valid_url('url'), implicit_return=False)
    def fetch_url(url: str):
      return f'Fetching {url}'

    result = fetch_url('http://example.com')
    assert 'Fetching' in result

  def test_valid_https_url(self):
    """Test guard passes for valid HTTPS URL."""

    @guarded_expression(valid_url('url'), implicit_return=False)
    def fetch_url(url: str):
      return f'Fetching {url}'

    result = fetch_url('https://example.com/path?query=value')
    assert 'Fetching' in result

  def test_url_without_scheme_fails(self):
    """Test guard fails for URL without scheme when require_scheme=True."""

    @guarded_expression(valid_url('url', require_scheme=True), implicit_return=False)
    def fetch_url(url: str):
      return f'Fetching {url}'

    with pytest.raises(GuardClauseError, match='must include a scheme'):
      fetch_url('example.com')

  def test_url_without_scheme_allowed(self):
    """Test guard passes for URL without scheme when require_scheme=False."""

    @guarded_expression(valid_url('url', require_scheme=False), implicit_return=False)
    def fetch_url(url: str):
      return f'Fetching {url}'

    result = fetch_url('example.com/path')
    assert 'Fetching' in result

  def test_invalid_url_fails(self):
    """Test guard fails for completely invalid URL."""

    @guarded_expression(valid_url('url'), implicit_return=False)
    def fetch_url(url: str):
      return f'Fetching {url}'

    with pytest.raises(GuardClauseError, match='must include a scheme'):
      fetch_url('   ')
