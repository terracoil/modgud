"""Guard checking logic for runtime validation.

GuardAdapter encapsulates guard evaluation (with optional `continuance`
budget for collecting additional failures) and dispatches the collected
failures through the chosen `GuardFailureEnum`. It is the Idunn adapter for
`GuardPort`.
"""

import functools
import inspect
from typing import Any, Callable

from idunn import Adapter, LifecycleEnum

from modgud.domain.enums import GuardFailureEnum
from modgud.domain.errors import GuardClauseError
from modgud.domain.ports import GuardPort
from modgud.domain.types import GuardFunction


@Adapter(GuardPort, lifecycle=LifecycleEnum.SINGLETON)
class GuardAdapter(GuardPort):
  """Runtime guard checking and failure handling."""

  def wrap_function(
    self,
    func: Callable[..., Any],
    guards: tuple[GuardFunction, ...],
    strategy: GuardFailureEnum,
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

    When ``func`` is a method (its first parameter is ``self`` or ``cls``), the guards see
    the call's arguments without the receiver, exactly as they would for a plain function.
    ``CALL_HANDLER`` handlers still receive the full argument list.
    """
    receiver: str | None = self._receiver_name(func)
    signature: inspect.Signature | None = self._signature_of(func)

    def dispatch(args: tuple[Any, ...], kwargs: dict[str, Any]) -> tuple[list[str], Any]:
      skip: int = 1 if receiver is not None and receiver not in kwargs else 0
      seen_by_guards = self._with_defaults(signature, args, kwargs)
      errors = self.check_guards(guards, args[skip:], seen_by_guards, continuance)
      outcome: Any = (
        None if not errors else self.handle_failure(errors, strategy, on_failure, args, kwargs)
      )
      return errors, outcome

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
      errors, outcome = dispatch(args, kwargs)
      return func(*args, **kwargs) if not errors else outcome

    @functools.wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
      # Guards are checked when the coroutine runs, so a non-raising strategy's fallback value
      # comes back from `await`, instead of a plain value the caller cannot await.
      errors, outcome = dispatch(args, kwargs)
      return await func(*args, **kwargs) if not errors else outcome

    wrapper = async_wrapper if inspect.iscoroutinefunction(func) else wrapper
    eager: dict[str, Any] | None = getattr(func, '__annotations__', None)
    if getattr(func, '__annotate__', None) is None and eager is not None:
      # Python 3.14's functools.wraps copies the lazy __annotate__ hook, not __annotations__;
      # a function whose annotations were set eagerly (e.g. by the transformer) has no hook.
      wrapper.__annotations__ = dict(eager)
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
    strategy: GuardFailureEnum,
    on_failure: Any,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
  ) -> Any:
    """Dispatch collected failures per strategy.

    :returns: Whatever the strategy yields (for RETURN_VALUE / ERROR_RETURN /
              CALL_HANDLER). ERROR_RAISE never returns - it raises.
    """
    if strategy is GuardFailureEnum.ERROR_RAISE:
      raise cls._build_exception(errors, on_failure)
    if strategy is GuardFailureEnum.ERROR_RETURN:
      result: Any = cls._build_exception(errors, on_failure)
    elif strategy is GuardFailureEnum.RETURN_VALUE:
      result = on_failure
    else:  # CALL_HANDLER
      result = on_failure(errors, *args, **kwargs)
    return result

  @staticmethod
  def _signature_of(func: Callable[..., Any]) -> inspect.Signature | None:
    """Return ``func``'s signature, or ``None`` for callables that don't expose one."""
    try:
      signature: inspect.Signature | None = inspect.signature(func)
    except (TypeError, ValueError):
      signature = None
    return signature

  @staticmethod
  def _with_defaults(
    signature: inspect.Signature | None, args: tuple[Any, ...], kwargs: dict[str, Any]
  ) -> dict[str, Any]:
    """Return ``kwargs`` plus, by name, every parameter the caller left at its default.

    Guards look parameters up by name first, so a default the caller never typed is still
    visible to ``positive('x')``. Positional arguments are passed through untouched.
    """
    defaults: dict[str, Any] = {}
    if signature is not None:
      try:
        supplied: set[str] = set(signature.bind_partial(*args, **kwargs).arguments)
      except TypeError:  # the call itself is malformed; let the real call report it
        supplied = set(signature.parameters)
      defaults = {
        name: parameter.default
        for name, parameter in signature.parameters.items()
        if name not in supplied and parameter.default is not inspect.Parameter.empty
      }
    return {**defaults, **kwargs}

  @staticmethod
  def _receiver_name(func: Callable[..., Any]) -> str | None:
    """Return ``'self'`` / ``'cls'`` when ``func`` is a method declaring one as its first parameter.

    "Method" means defined in a class body: the part of ``__qualname__`` after the last
    ``<locals>`` has a dot in it. A module-level ``def factory(cls, n)`` keeps all its arguments.
    """
    qualname_tail: str = getattr(func, '__qualname__', '').rsplit('<locals>.', 1)[-1]
    try:
      first: inspect.Parameter | None = next(
        iter(inspect.signature(func).parameters.values()), None
      )
    except (TypeError, ValueError):
      first = None
    positional = (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
    is_receiver: bool = (
      '.' in qualname_tail
      and first is not None
      and first.name in ('self', 'cls')
      and first.kind in positional
    )
    return first.name if is_receiver and first is not None else None

  @staticmethod
  def _build_exception(errors: list[str], exc_class: Any) -> BaseException:
    """Build a single exception or ExceptionGroup from collected errors."""
    cls_to_use: type[Exception] = exc_class if isinstance(exc_class, type) else GuardClauseError
    return (
      cls_to_use(errors[0])
      if len(errors) == 1
      else ExceptionGroup('Guards failed', [cls_to_use(m) for m in errors])
    )
