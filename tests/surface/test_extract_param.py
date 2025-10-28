"""Tests for the public CommonGuards.extract_param utility method."""

from modgud import CommonGuards


class TestExtractParam:
  """Tests for CommonGuards.extract_param utility for custom guard authors."""

  def test_extract_from_kwargs(self):
    """Test extracting parameter from kwargs."""
    args = ()
    kwargs = {'username': 'alice', 'email': 'alice@example.com'}

    result = CommonGuards.extract_param('username', 0, args, kwargs)
    assert result == 'alice'

  def test_extract_from_args_explicit_position(self):
    """Test extracting parameter from args with explicit position."""
    args = ('alice', 'alice@example.com')
    kwargs = {}

    result = CommonGuards.extract_param('username', 0, args, kwargs)
    assert result == 'alice'

    result = CommonGuards.extract_param('email', 1, args, kwargs)
    assert result == 'alice@example.com'

  def test_extract_from_args_default_position(self):
    """Test extracting parameter from args with default position (0)."""
    args = ('alice',)
    kwargs = {}

    result = CommonGuards.extract_param('username', None, args, kwargs)
    assert result == 'alice'

  def test_extract_with_default_value(self):
    """Test extraction returns default when parameter not found."""
    args = ()
    kwargs = {}

    result = CommonGuards.extract_param('username', 0, args, kwargs, default='anonymous')
    assert result == 'anonymous'

  def test_kwargs_takes_precedence_over_args(self):
    """Test that kwargs value takes precedence over args."""
    args = ('positional_value',)
    kwargs = {'username': 'keyword_value'}

    result = CommonGuards.extract_param('username', 0, args, kwargs)
    assert result == 'keyword_value'

  def test_out_of_bounds_position_uses_default(self):
    """Test that out-of-bounds position returns default."""
    args = ('alice',)
    kwargs = {}

    result = CommonGuards.extract_param('email', 5, args, kwargs, default=None)
    assert result is None

  def test_custom_guard_example(self):
    """Test using CommonGuards.extract_param in a custom guard implementation."""

    def check_positive_amount(*args, **kwargs):
      """Check for positive amount."""
      value = CommonGuards.extract_param('amount', 0, args, kwargs, default=0)
      return value > 0 or f'amount must be positive, got {value}'

    # Test with positional arg
    result = check_positive_amount(100)
    assert result is True

    # Test with keyword arg
    result = check_positive_amount(amount=50)
    assert result is True

    # Test failure
    result = check_positive_amount(-10)
    assert result == 'amount must be positive, got -10'

    # Test with default (0)
    result = check_positive_amount()
    assert result == 'amount must be positive, got 0'

  def test_convenience_export_works(self):
    """Test that extract_param is exported at module level for convenience."""
    from modgud import extract_param

    # Should work the same as CommonGuards.extract_param
    args = ('alice',)
    kwargs = {}

    result = extract_param('username', 0, args, kwargs)
    assert result == 'alice'

    # Should be the same function
    assert extract_param is CommonGuards.extract_param
