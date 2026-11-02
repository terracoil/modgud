"""Swap the engine: pass your own ``runtime=`` / ``transformer=`` typed against modgud's ports.

Idunn injects the real adapters; an explicit argument always wins, so this is the seam for
tests and instrumentation. (``IDUNN_ENV`` and ``Idunn().reset()`` steer discovery; not needed.)

Run: poetry run python examples/free_range/12_swapping_the_runtime.py
See: docs/api-reference.md#integration-seam
"""

from typing import Any, Callable, TypeVar

from modgud import (
  GuardFailureEnum,
  GuardFunction,
  GuardRuntimePort,
  ImplicitReturnTransformerPort,
  guarded_expression,
)

T = TypeVar('T')


class AuditingRuntime:
  """Runtime fake that logs each call's guard verdicts and never blocks."""

  def __init__(self) -> None:
    """Start with an empty audit log."""
    self.log: list[str] = []

  def wrap_function(
    self,
    func: Callable[..., Any],
    guards: tuple[GuardFunction, ...],
    strategy: GuardFailureEnum,
    on_failure: Any,
    continuance: int,
  ) -> Callable[..., Any]:
    """Wrap ``func`` so each call records the guards' answers, then runs regardless."""

    def audited(*args: Any, **kwargs: Any) -> Any:
      verdicts: list[bool | str] = [guard(*args, **kwargs) for guard in guards]
      self.log.append(f'{func.__name__}({", ".join(map(repr, args))}) -> {verdicts}')
      return func(*args, **kwargs)

    return audited


class RecordingTransformer:
  """Transformer fake: notes each function it is handed and returns it untouched."""

  def __init__(self) -> None:
    """Start with nothing seen."""
    self.seen: list[str] = []

  def transform_function(self, func: Callable[..., T]) -> Callable[..., T]:
    """Record ``func`` and skip the AST rewrite entirely."""
    self.seen.append(func.__name__)
    return func


AUDIT = AuditingRuntime()
RECORDER = RecordingTransformer()
RUNTIME: GuardRuntimePort = AUDIT  # mypy checks each fake against its port here
TRANSFORMER: ImplicitReturnTransformerPort = RECORDER


@guarded_expression(
  lambda x: x > 0 or 'x must be positive', runtime=RUNTIME, transformer=TRANSFORMER
)
def halve(x: int) -> float:
  """Halve ``x``; the explicit ``return`` is fine because the fake skips the rewrite."""
  return x / 2


if __name__ == '__main__':
  assert halve(8) == 4.0
  assert halve(-8) == -4.0  # the auditing runtime lets refusals through
  assert AUDIT.log == ['halve(8) -> [True]', "halve(-8) -> ['x must be positive']"]
  assert RECORDER.seen == ['halve']

  print('audit log:', *AUDIT.log, sep='\n  ')
  print(f'transformer saw: {RECORDER.seen}')
