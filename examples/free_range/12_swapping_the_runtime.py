"""Swap the engine: pass your own ``guard_port=`` / ``imp_return_port=`` typed against modgud's ports.

Idunn injects the real adapters; an explicit argument always wins, so this is the seam for
tests and instrumentation. (``IDUNN_ENV`` and ``Idunn().reset()`` steer discovery; not needed.)

Run: poetry run python examples/free_range/12_swapping_the_runtime.py
See: docs/api-reference.md#integration-seam
"""

from collections.abc import Mapping
from typing import Any, Callable, TypeVar

from modgud import (
  EopPort,
  GuardFailureEnum,
  GuardFunction,
  GuardPort,
  ImplicitReturnPort,
  guarded_expression,
)

T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])


class AuditingRuntime:
  """Guard-port fake that logs each call's guard verdicts and never blocks."""

  def __init__(self) -> None:
    """Start with an empty audit log."""
    self.log: list[str] = []

  def transform(
    self,
    func: Callable[..., Any],
    continuance: int,
    imp_return_port: ImplicitReturnPort,
    implicit_return: bool,
    guards: tuple[GuardFunction, ...],
    strategy: GuardFailureEnum,
    on_failure: Any,
    forms: Mapping[Any, EopPort],
  ) -> Callable[..., Any]:
    """Wrap ``func`` so each call records the guards' answers, then runs regardless."""
    target: Callable[..., Any] = imp_return_port.transform_function(
      func, forms=forms, implicit_return=implicit_return
    )

    def audited(*args: Any, **kwargs: Any) -> Any:
      verdicts: list[bool | str] = [guard(*args, **kwargs) for guard in guards]
      self.log.append(f'{target.__name__}({", ".join(map(repr, args))}) -> {verdicts}')
      return target(*args, **kwargs)

    return audited


class RecordingTransformer:
  """Implicit-return fake: notes each function it is handed and returns it untouched."""

  def __init__(self) -> None:
    """Start with nothing seen."""
    self.seen: list[str] = []

  def transform(self, func: F, *, forms: Mapping[Any, EopPort]) -> F:
    """Record ``func`` (as ``@implicit_return()`` would hand it over) and skip the rewrite."""
    self.seen.append(func.__name__)
    return func

  def transform_function(
    self, func: Callable[..., T], *, forms: Mapping[Any, EopPort], implicit_return: bool = True
  ) -> Callable[..., T]:
    """Record ``func`` (as a guard port hands it over) and skip the AST rewrite entirely."""
    self.seen.append(func.__name__)
    return func


AUDIT = AuditingRuntime()
RECORDER = RecordingTransformer()
GUARD_PORT: GuardPort = AUDIT  # mypy checks each fake against its port here
IMP_RETURN_PORT: ImplicitReturnPort = RECORDER


@guarded_expression(
  lambda x: x > 0 or 'x must be positive', guard_port=GUARD_PORT, imp_return_port=IMP_RETURN_PORT
)
def halve(x: int) -> float:
  """Halve ``x``; the explicit ``return`` is fine because the fake skips the rewrite."""
  return x / 2


if __name__ == '__main__':
  assert halve(8) == 4.0
  assert halve(-8) == -4.0  # the auditing guard port lets refusals through
  assert AUDIT.log == ['halve(8) -> [True]', "halve(-8) -> ['x must be positive']"]
  assert RECORDER.seen == ['halve']

  print('audit log:', *AUDIT.log, sep='\n  ')
  print(f'transformer saw: {RECORDER.seen}')
