"""Unified guarded_expression decorator combining guards and implicit returns.

`guarded_expression` is the primary modgud decorator. It applies guard
clauses to a function and, by default, also performs the implicit-return
AST rewrite so the last expression in each branch is returned automatically.
Strict mode: if `implicit_return=True` and the AST rewrite refuses (source
unavailable, unsupported construct, etc.), the exception propagates from
the decoration site.
"""

from typing import Any, Callable

from modgud.domain import GuardClauseError, GuardFailureStrategy
from modgud.infrastructure import GuardRuntime, ImplicitReturnTransformer
from modgud.shared import GuardFunction


def guarded_expression(
  *guards: GuardFunction,
  implicit_return: bool = True,
  strategy: GuardFailureStrategy = GuardFailureStrategy.ERROR_RAISE,
  on_failure: Any = GuardClauseError,
  continuance: int = 0,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
  """Guard a function and, by default, enable implicit returns.

  Guards return ``True`` (pass) or an error message string (fail).
  Failures are dispatched per ``strategy``; the payload paired with the
  strategy is ``on_failure``:

  - ``ERROR_RAISE`` (default): ``on_failure`` is the exception class to raise.
  - ``ERROR_RETURN``: same exception, returned instead of raised.
  - ``RETURN_VALUE``: ``on_failure`` returned as-is.
  - ``CALL_HANDLER``: ``on_failure(errors, *args, **kwargs)`` is called.

  ``continuance`` caps how many guards past the first failure are evaluated.
  """

  def _decorator(func: Callable[..., Any]) -> Callable[..., Any]:
    already_transformed = getattr(func, '__implicit_return__', False)
    target = (
      ImplicitReturnTransformer.transform_function(func)
      if implicit_return and not already_transformed
      else func
    )
    wrapped = GuardRuntime.wrap_function(target, guards, strategy, on_failure, continuance)
    if implicit_return:
      wrapped.__implicit_return__ = True  # type: ignore[attr-defined]
    return wrapped

  return _decorator
