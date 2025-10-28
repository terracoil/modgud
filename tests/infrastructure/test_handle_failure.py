"""Tests for guard failure handling strategies."""

from modgud.domain.models.errors import GuardClauseError
from modgud.infrastructure.adapters.guard_checker_adapter import GuardCheckerAdapter


class TestHandleFailure:
  """Tests for guard failure handling strategies."""

  def test_handle_failure_exception_class(self):
    """Test handle_failure with exception class."""
    result, exception = GuardCheckerAdapter.handle_failure(
      'Test error', ValueError, 'test_func', (1, 2), {}, False
    )
    assert result is None
    assert isinstance(exception, ValueError)
    assert str(exception) == 'Test error'

  def test_handle_failure_custom_value(self):
    """Test handle_failure with custom return value."""
    result, exception = GuardCheckerAdapter.handle_failure(
      'Test error', {'error': 'custom'}, 'test_func', (1, 2), {}, False
    )
    assert result == {'error': 'custom'}
    assert exception is None

  def test_handle_failure_callable(self):
    """Test handle_failure with callable handler."""

    def handler(msg, *args, **kwargs):
      return f'Handled: {msg}'

    result, exception = GuardCheckerAdapter.handle_failure(
      'Test error', handler, 'test_func', (1, 2), {}, False
    )
    assert result == 'Handled: Test error'
    assert exception is None

  def test_handle_failure_guard_clause_error(self):
    """Test handle_failure with GuardClauseError."""
    result, exception = GuardCheckerAdapter.handle_failure(
      'Test error', GuardClauseError, 'test_func', (1, 2), {}, False
    )
    assert result is None
    assert isinstance(exception, GuardClauseError)
    assert str(exception) == 'Test error'

  def test_handle_failure_none_value(self):
    """Test handle_failure with None as on_error value."""
    result, exception = GuardCheckerAdapter.handle_failure(
      'Test error', None, 'test_func', (1, 2), {}, False
    )
    assert result is None
    assert exception is None

  def test_handle_failure_with_logging(self, caplog):
    """Test handle_failure logs when log=True."""
    import logging

    caplog.set_level(logging.INFO)

    result, exception = GuardCheckerAdapter.handle_failure(
      'Validation failed',
      None,
      'process_user',
      (1, 2),
      {'name': 'test'},
      True,  # log_enabled=True
    )

    # Verify logging occurred
    assert len(caplog.records) == 1
    assert 'Guard clause failed in process_user: Validation failed' in caplog.text
    assert caplog.records[0].levelname == 'INFO'

    # Verify normal behavior
    assert result is None
    assert exception is None
