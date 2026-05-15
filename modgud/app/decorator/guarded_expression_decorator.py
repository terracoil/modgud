"""Unified guarded_expression decorator combining guards and implicit returns.

`guarded_expression` is the primary modgud decorator. It applies guard
clauses to a function and, by default, also performs the implicit-return
AST rewrite so the last expression in each branch is returned automatically.
"""

from typing import Any, Callable

from modgud.domain import (
  GuardClauseError,
  GuardFailureStrategy,
  GuardFunction,
  UnsupportedConstructError,
)
from modgud.infrastructure import GuardRuntime
from modgud.infrastructure.transform import ImplicitReturnTransformer


class guarded_expression:
  """Guard a function and (optionally) enable implicit returns.

  Guards are callables returning `True` on success or an error message
  string on failure. The way failures are dispatched is controlled by
  `strategy`; the payload paired with the strategy lives in `on_failure`:

  - `ERROR_RAISE` (default): `on_failure` is the exception class to raise.
    Default class is `GuardClauseError`.
  - `ERROR_RETURN`: same exception, but *returned* instead of raised.
  - `RETURN_VALUE`: `on_failure` is the value returned as-is.
  - `CALL_HANDLER`: `on_failure(errors, *args, **kwargs)` is called; its
    return value is returned to the caller.

  `continuance` caps how many *additional* guards are evaluated past the
  first failure (default 0 = stop immediately). When more than one failure
  is collected, `ERROR_RAISE`/`ERROR_RETURN` wrap the instances in an
  `ExceptionGroup('Guards failed', [...])`.

  :param guards: Variable-length guard functions.
  :param implicit_return: Apply the implicit-return AST rewrite (default True).
  :param strategy: How to dispatch failures (default ERROR_RAISE).
  :param on_failure: Exception class / value / handler paired with strategy.
  :param continuance: Extra guards to evaluate after the first failure.

  Example::

      @guarded_expression(
        positive('x'),
        strategy=GuardFailureStrategy.RETURN_VALUE,
        on_failure=-1,
      )
      def safe_divide(x):
        100 / x
  """

  def __init__(
    self,
    *guards: GuardFunction,
    implicit_return: bool = True,
    strategy: GuardFailureStrategy = GuardFailureStrategy.ERROR_RAISE,
    on_failure: Any = GuardClauseError,
    continuance: int = 0,
  ) -> None:
    """Capture decorator configuration."""
    self.guards = guards
    self.implicit_return_enabled = implicit_return
    self.strategy = strategy
    self.on_failure = on_failure
    self.continuance = continuance

  def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
    """Apply guard wrapping and optional implicit-return transformation."""
    target = func
    if self.implicit_return_enabled:
      try:
        target = ImplicitReturnTransformer.transform_function(func)
      except (UnsupportedConstructError, ValueError, OSError):
        pass
    wrapped = GuardRuntime.wrap_function(
      target, self.guards, self.strategy, self.on_failure, self.continuance
    )
    if self.implicit_return_enabled:
      wrapped.__implicit_return__ = True  # type: ignore[attr-defined]
    return wrapped
