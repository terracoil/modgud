"""Guard checking logic for runtime validation.

GuardRuntime encapsulates guard evaluation (with optional `continuance`
budget for collecting additional failures) and dispatches the collected
failures through the chosen `GuardFailureStrategy`.
"""

import functools
from typing import Any, Callable

from modgud.domain import GuardClauseError, GuardFailureStrategy
from modgud.shared import GuardFunction


class GuardRuntime:
  """Runtime guard checking and failure handling."""

  @classmethod
  def wrap_function(
    cls,
    func: Callable[..., Any],
    guards: tuple[GuardFunction, ...],
    strategy: GuardFailureStrategy,
    on_failure: Any,
    continuance: int,
  ) -> Callable[..., Any]:
    """Wrap a function with guard checking.

    :param func: Function to wrap.
    :param guards: Guards evaluated before each call.
    :param strategy: How to dispatch collected failures.
    :param on_failure: Exception class / value / handler paired with strategy.
    :param continuance: Max additional guards to evaluate past the first failure.
    :returns: Wrapped function.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
      errors = cls.check_guards(guards, args, kwargs, continuance)
      if not errors:
        result = func(*args, **kwargs)
      else:
        result = cls.handle_failure(errors, strategy, on_failure, args, kwargs)
      return result

    wrapper.__dict__.update(func.__dict__)
    return wrapper

  @classmethod
  def check_guards(
    cls,
    guards: tuple[GuardFunction, ...],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    continuance: int,
  ) -> list[str]:
    """Evaluate guards, collecting up to (1 + continuance) failures.

    A guard that *raises* (rather than returning True/str) terminates the
    sweep: if no failures have been recorded yet, the exception propagates
    (it's a programming error in the guard itself); otherwise we treat it
    as cascade fallout from already-invalid input and stop collecting.

    :returns: List of error message strings; empty when all guards pass.
    """
    errors: list[str] = []
    for guard in guards:
      if len(errors) > continuance:
        break
      try:
        result = guard(*args, **kwargs)
      except Exception:
        if not errors:
          raise
        break
      if result is not True:
        errors.append(result if isinstance(result, str) else 'Guard clause failed')
    return errors

  @classmethod
  def handle_failure(
    cls,
    errors: list[str],
    strategy: GuardFailureStrategy,
    on_failure: Any,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
  ) -> Any:
    """Dispatch collected failures per strategy.

    :returns: Whatever the strategy yields (for RETURN_VALUE / ERROR_RETURN /
              CALL_HANDLER). ERROR_RAISE never returns - it raises.
    """
    if strategy is GuardFailureStrategy.ERROR_RAISE:
      raise cls._build_exception(errors, on_failure)
    if strategy is GuardFailureStrategy.ERROR_RETURN:
      result: Any = cls._build_exception(errors, on_failure)
    elif strategy is GuardFailureStrategy.RETURN_VALUE:
      result = on_failure
    else:  # CALL_HANDLER
      result = on_failure(errors, *args, **kwargs)
    return result

  @staticmethod
  def _build_exception(errors: list[str], exc_class: Any) -> BaseException:
    """Build a single exception or ExceptionGroup from collected errors."""
    cls_to_use = exc_class if isinstance(exc_class, type) else GuardClauseError
    if len(errors) == 1:
      return cls_to_use(errors[0])
    return ExceptionGroup('Guards failed', [cls_to_use(m) for m in errors])
