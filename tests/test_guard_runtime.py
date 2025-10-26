"""Unit tests for guard runtime logic."""

from modgud.guarded_expression.guard_runtime import check_guards, handle_failure
from modgud.shared.errors import GuardClauseError


def test_check_guards_all_pass():
  """Test that check_guards returns None when all guards pass."""
  guards = (
    lambda x: x > 0 or "Must be positive",
    lambda x: x < 100 or "Must be less than 100",
  )
  result = check_guards(guards, (50,), {})
  assert result is None


def test_check_guards_first_fails():
  """Test that check_guards returns error message from first failed guard."""
  guards = (
    lambda x: x > 0 or "Must be positive",
    lambda x: x < 100 or "Must be less than 100",
  )
  result = check_guards(guards, (-5,), {})
  assert result == "Must be positive"


def test_check_guards_second_fails():
  """Test that check_guards returns error message from second failed guard."""
  guards = (
    lambda x: x > 0 or "Must be positive",
    lambda x: x < 100 or "Must be less than 100",
  )
  result = check_guards(guards, (150,), {})
  assert result == "Must be less than 100"


def test_check_guards_boolean_false():
  """Test that check_guards handles boolean False guard result."""
  guards = (lambda x: False,)
  result = check_guards(guards, (5,), {})
  assert result == "Guard clause failed"


def test_handle_failure_exception_class():
  """Test handle_failure with exception class."""
  result, exception = handle_failure(
    "Test error",
    ValueError,
    "test_func",
    (1, 2),
    {},
    False
  )
  assert result is None
  assert isinstance(exception, ValueError)
  assert str(exception) == "Test error"


def test_handle_failure_custom_value():
  """Test handle_failure with custom return value."""
  result, exception = handle_failure(
    "Test error",
    {"error": "custom"},
    "test_func",
    (1, 2),
    {},
    False
  )
  assert result == {"error": "custom"}
  assert exception is None


def test_handle_failure_callable():
  """Test handle_failure with callable handler."""
  def handler(msg, *args, **kwargs):
    return f"Handled: {msg}"

  result, exception = handle_failure(
    "Test error",
    handler,
    "test_func",
    (1, 2),
    {},
    False
  )
  assert result == "Handled: Test error"
  assert exception is None


def test_handle_failure_guard_clause_error():
  """Test handle_failure with GuardClauseError."""
  result, exception = handle_failure(
    "Test error",
    GuardClauseError,
    "test_func",
    (1, 2),
    {},
    False
  )
  assert result is None
  assert isinstance(exception, GuardClauseError)
  assert str(exception) == "Test error"


def test_handle_failure_none_value():
  """Test handle_failure with None as on_error value."""
  result, exception = handle_failure(
    "Test error",
    None,
    "test_func",
    (1, 2),
    {},
    False
  )
  assert result is None
  assert exception is None


# Guard runtime logging test (coverage improvement)
def test_handle_failure_with_logging(caplog):
  """Test handle_failure logs when log=True."""
  import logging
  caplog.set_level(logging.INFO)

  result, exception = handle_failure(
    "Validation failed",
    None,
    "process_user",
    (1, 2),
    {"name": "test"},
    True  # log_enabled=True
  )

  # Verify logging occurred
  assert len(caplog.records) == 1
  assert "Guard clause failed in process_user: Validation failed" in caplog.text
  assert caplog.records[0].levelname == "INFO"

  # Verify normal behavior
  assert result is None
  assert exception is None
