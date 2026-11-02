"""Idunn wiring: bootstrap, injection of the two ports, singletons, reset, and the fake seam."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any, Callable

import pytest
from idunn import Idunn
from modgud.app import guarded_expression, implicit_return
from modgud.app.wiring import Wiring
from modgud.domain.guarded_expr import GuardClauseError
from modgud.domain.guarded_expr.ports import GuardRuntimePort
from modgud.domain.implicit_ret.ports import ImplicitReturnTransformerPort


class RecordingTransformer:
  """Transformer fake: records each function it is asked to transform and returns it as-is."""

  def __init__(self) -> None:
    """Start with nothing recorded."""
    self.seen: list[Callable[..., Any]] = []

  def transform_function(self, func: Callable[..., Any]) -> Callable[..., Any]:
    """Record ``func`` and hand it back unchanged."""
    self.seen.append(func)
    return func


@pytest.fixture(autouse=True)
def _reset_idunn() -> Iterator[None]:
  """Isolate the Idunn singleton without pinning (or overriding) the active environment."""
  Idunn().reset(environment=Idunn().environment)
  yield
  Idunn().reset(environment=Idunn().environment)


class TestBootstrap:
  """``Wiring.ensure()`` discovers modgud's ports and adapters once."""

  def test_report_lists_both_adapters_and_both_ports(self) -> None:
    report = Wiring.ensure()

    assert report['root_package'] == 'modgud'
    assert set(report['registered_adapters']) == {
      'modgud.infrastructure.adapters.guard_runtime.GuardRuntime',
      'modgud.infrastructure.adapters.implicit_return_transformer.ImplicitReturnTransformer',
    }
    assert set(report['registered_ports']) == {
      'modgud.domain.guarded_expr.ports.guard_runtime_port.GuardRuntimePort',
      'modgud.domain.implicit_ret.ports.implicit_return_transformer_port.'
      'ImplicitReturnTransformerPort',
    }

  def test_second_bootstrap_returns_the_cached_report(self) -> None:
    first = Idunn().bootstrap('modgud')

    assert Idunn().bootstrap('modgud') is first

  def test_wiring_ensure_twice_returns_the_same_report(self) -> None:
    assert Wiring.ensure() is Wiring.ensure()


class TestInjection:
  """The decorators receive their adapters through ``@Invert``."""

  def test_guarded_expression_receives_both_ports(self) -> None:
    decorator = guarded_expression()

    assert isinstance(decorator.runtime, GuardRuntimePort)
    assert isinstance(decorator.transformer, ImplicitReturnTransformerPort)

  def test_implicit_return_receives_the_transformer_port(self) -> None:
    assert isinstance(implicit_return().transformer, ImplicitReturnTransformerPort)

  def test_adapters_are_singletons_shared_across_decorators(self) -> None:
    first, second = guarded_expression(), guarded_expression()

    assert first.runtime is second.runtime
    assert first.transformer is second.transformer
    assert implicit_return().transformer is first.transformer


class TestReset:
  """``Idunn().reset()`` forgets the wiring; the next decoration re-discovers it."""

  def test_decoration_still_works_after_reset(self) -> None:
    before = guarded_expression().runtime
    Idunn().reset(environment=Idunn().environment)

    @guarded_expression(lambda x: x > 0 or 'x must be positive', implicit_return=False)
    def double(x: int) -> int:
      return x * 2

    assert double(2) == 4
    with pytest.raises(GuardClauseError, match='x must be positive'):
      double(-1)
    assert guarded_expression().runtime is not before


class TestFakeSeam:
  """A caller-supplied port implementation wins over the injected adapter."""

  def test_guarded_expression_uses_a_supplied_transformer(self) -> None:
    fake = RecordingTransformer()

    def triple(x: int) -> int:
      return x * 3

    decorated = guarded_expression(transformer=fake)(triple)

    assert fake.seen == [triple]
    assert decorated(2) == 6

  def test_implicit_return_uses_a_supplied_transformer(self) -> None:
    fake = RecordingTransformer()

    def identity(x: int) -> int:
      return x

    decorated = implicit_return(transformer=fake)(identity)

    assert fake.seen == [identity]
    assert decorated is identity
