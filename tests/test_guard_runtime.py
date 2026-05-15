"""Unit tests for GuardRuntime: check_guards + handle_failure."""

import pytest
from modgud import GuardClauseError, GuardFailureStrategy
from modgud.infrastructure.guard_runtime import GuardRuntime


class TestCheckGuards:
  """Tests for guard evaluation with the continuance budget."""

  def test_all_pass_returns_empty_list(self):
    """Empty error list when every guard returns True."""
    guards = (
      lambda x: x > 0 or 'Must be positive',
      lambda x: x < 100 or 'Must be less than 100',
    )
    result = GuardRuntime.check_guards(guards, (50,), {}, continuance=0)
    assert result == []

  def test_fail_fast_stops_at_first_failure(self):
    """With continuance=0, evaluation stops at the first failed guard."""
    seen = []

    def guard_a(x):
      seen.append('a')
      return x > 0 or 'Must be positive'

    def guard_b(x):
      seen.append('b')
      return x < 100 or 'Must be less than 100'

    result = GuardRuntime.check_guards((guard_a, guard_b), (-5,), {}, continuance=0)
    assert result == ['Must be positive']
    assert seen == ['a']  # guard_b never invoked

  def test_continuance_collects_additional_failures(self):
    """continuance=N evaluates up to N more guards past the first failure."""
    guards = (
      lambda x: 'first fail',
      lambda x: 'second fail',
      lambda x: 'third fail',
      lambda x: 'fourth fail',
    )
    result = GuardRuntime.check_guards(guards, (0,), {}, continuance=2)
    assert result == ['first fail', 'second fail', 'third fail']

  def test_continuance_zero_collects_only_first(self):
    """continuance=0 (default) caps the list at a single failure."""
    guards = tuple(lambda x, _i=i: f'fail {_i}' for i in range(5))
    result = GuardRuntime.check_guards(guards, (0,), {}, continuance=0)
    assert result == ['fail 0']

  def test_non_string_failure_normalised(self):
    """A guard returning a non-True non-string yields the generic message."""
    guards = (lambda x: False,)
    result = GuardRuntime.check_guards(guards, (5,), {}, continuance=0)
    assert result == ['Guard clause failed']

  def test_raising_guard_propagates_when_no_prior_failure(self):
    """A raising guard with empty errors propagates the exception."""

    def bad(*args, **kwargs):
      raise RuntimeError('guard exploded')

    with pytest.raises(RuntimeError, match='guard exploded'):
      GuardRuntime.check_guards((bad,), (1,), {}, continuance=3)

  def test_raising_guard_stops_collection_after_first_failure(self):
    """During the continuance window, a raising guard halts collection (cascade safety)."""
    guards = (
      lambda x: 'first fail',
      lambda x: (_ for _ in ()).throw(AttributeError('cascade')),
    )
    # Should not raise; just stops collecting and returns what we have.
    result = GuardRuntime.check_guards(guards, (None,), {}, continuance=2)
    assert result == ['first fail']


class TestHandleFailure:
  """Tests for failure dispatch through GuardFailureStrategy."""

  def test_error_raise_single(self):
    """ERROR_RAISE with one failure raises the on_failure class."""
    with pytest.raises(GuardClauseError, match='boom'):
      GuardRuntime.handle_failure(
        ['boom'], GuardFailureStrategy.ERROR_RAISE, GuardClauseError, (), {}
      )

  def test_error_raise_multiple_uses_exception_group(self):
    """ERROR_RAISE with multiple failures raises an ExceptionGroup."""
    with pytest.raises(ExceptionGroup) as exc:
      GuardRuntime.handle_failure(
        ['a', 'b', 'c'], GuardFailureStrategy.ERROR_RAISE, GuardClauseError, (), {}
      )
    assert exc.value.message == 'Guards failed'
    assert len(exc.value.exceptions) == 3
    assert all(isinstance(e, GuardClauseError) for e in exc.value.exceptions)
    assert [str(e) for e in exc.value.exceptions] == ['a', 'b', 'c']

  def test_error_raise_custom_exception_class(self):
    """ERROR_RAISE respects a custom exception class in on_failure."""
    with pytest.raises(ValueError, match='nope'):
      GuardRuntime.handle_failure(['nope'], GuardFailureStrategy.ERROR_RAISE, ValueError, (), {})

  def test_error_return_single_returns_instance(self):
    """ERROR_RETURN with one failure returns the exception instance."""
    result = GuardRuntime.handle_failure(
      ['err'], GuardFailureStrategy.ERROR_RETURN, GuardClauseError, (), {}
    )
    assert isinstance(result, GuardClauseError)
    assert str(result) == 'err'

  def test_error_return_multiple_returns_group(self):
    """ERROR_RETURN with multiple failures returns an ExceptionGroup."""
    result = GuardRuntime.handle_failure(
      ['a', 'b'], GuardFailureStrategy.ERROR_RETURN, GuardClauseError, (), {}
    )
    assert isinstance(result, ExceptionGroup)
    assert len(result.exceptions) == 2

  def test_return_value_returns_payload_as_is(self):
    """RETURN_VALUE returns on_failure verbatim."""
    sentinel = {'error': 'custom'}
    result = GuardRuntime.handle_failure(
      ['ignored'], GuardFailureStrategy.RETURN_VALUE, sentinel, (), {}
    )
    assert result is sentinel

  def test_return_value_none(self):
    """RETURN_VALUE handles None payload."""
    result = GuardRuntime.handle_failure(
      ['ignored'], GuardFailureStrategy.RETURN_VALUE, None, (), {}
    )
    assert result is None

  def test_call_handler_passes_errors_args_kwargs(self):
    """CALL_HANDLER invokes the handler with (errors, *args, **kwargs)."""
    captured = {}

    def handler(errors, *args, **kwargs):
      captured['errors'] = errors
      captured['args'] = args
      captured['kwargs'] = kwargs
      return 'handled'

    result = GuardRuntime.handle_failure(
      ['boom'], GuardFailureStrategy.CALL_HANDLER, handler, (1, 2), {'k': 'v'}
    )
    assert result == 'handled'
    assert captured['errors'] == ['boom']
    assert captured['args'] == (1, 2)
    assert captured['kwargs'] == {'k': 'v'}

  def test_call_handler_always_receives_list(self):
    """CALL_HANDLER receives a list even when there is only one failure."""
    received: list[list[str]] = []

    def handler(errors, *args, **kwargs):
      received.append(errors)
      return None

    GuardRuntime.handle_failure(['only one'], GuardFailureStrategy.CALL_HANDLER, handler, (), {})
    assert received == [['only one']]


class TestWrapFunctionIntegration:
  """End-to-end tests of wrap_function tying check_guards + handle_failure together."""

  def test_default_error_raise(self):
    """Wrap with default strategy raises GuardClauseError on failure."""

    def f(x):
      return x * 2

    wrapped = GuardRuntime.wrap_function(
      f,
      (lambda x: x > 0 or 'positive',),
      GuardFailureStrategy.ERROR_RAISE,
      GuardClauseError,
      0,
    )
    assert wrapped(3) == 6
    with pytest.raises(GuardClauseError, match='positive'):
      wrapped(-1)

  def test_body_not_executed_on_failure(self):
    """Wrapped body must not run when any guard fails."""
    calls = []

    def f(x):
      calls.append(x)
      return x

    wrapped = GuardRuntime.wrap_function(
      f,
      (lambda x: 'fail',),
      GuardFailureStrategy.RETURN_VALUE,
      'fallback',
      0,
    )
    assert wrapped(1) == 'fallback'
    assert calls == []

  def test_continuance_yields_exception_group(self):
    """continuance>0 with multiple failures produces an ExceptionGroup."""

    def f(x):
      return x

    wrapped = GuardRuntime.wrap_function(
      f,
      (lambda x: 'fail-a', lambda x: 'fail-b', lambda x: 'fail-c'),
      GuardFailureStrategy.ERROR_RAISE,
      GuardClauseError,
      2,
    )
    with pytest.raises(ExceptionGroup) as exc:
      wrapped(0)
    assert len(exc.value.exceptions) == 3
