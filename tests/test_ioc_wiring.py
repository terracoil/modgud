"""Idunn wiring: discovery on first use, injection of the two ports, singletons, reset, fakes."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any, Callable

import pytest
from idunn import Idunn
from modgud import (
  GuardClauseError,
  GuardPort,
  ImplicitReturnPort,
  guarded_expression,
  implicit_return,
)


class PassthroughRuntime:
  """Runtime fake: wraps nothing, so the decorated function is the one it was handed."""

  def wrap_function(
    self,
    func: Callable[..., Any],
    guards: tuple[Any, ...],
    strategy: Any,
    on_failure: Any,
    continuance: int,
  ) -> Callable[..., Any]:
    """Hand ``func`` back unguarded."""
    return func


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
  """The first decoration that needs a port discovers modgud's ports and adapters, once."""

  def test_nothing_is_wired_before_the_first_decoration(self) -> None:
    assert 'modgud' not in Idunn().describe()

  def test_the_first_decoration_discovers_both_adapters_and_both_ports(self) -> None:
    guarded_expression()
    report = Idunn().bootstrap('modgud')  # a cache hit: the decoration already discovered

    assert report['root_package'] == 'modgud'
    assert set(report['registered_adapters']) == {
      'modgud.infrastructure.adapters.guard_adapter.GuardAdapter',
      'modgud.infrastructure.adapters.implicit_return_adapter.ImplicitReturnAdapter',
    }
    assert set(report['registered_ports']) == {
      'modgud.domain.ports.guard_port.GuardPort',
      'modgud.domain.ports.implicit_return_port.ImplicitReturnPort',
    }

  def test_implicit_return_alone_discovers_too(self) -> None:
    implicit_return()

    assert 'ImplicitReturnAdapter' in Idunn().describe()

  def test_later_decorations_reuse_the_first_discovery(self) -> None:
    guarded_expression()
    first = Idunn().bootstrap('modgud')
    implicit_return()
    guarded_expression()

    assert Idunn().bootstrap('modgud') is first


class TestInjection:
  """The decorators receive their adapters through ``@Invert``."""

  def test_guarded_expression_receives_both_ports(self) -> None:
    decorator = guarded_expression()

    assert isinstance(decorator.runtime, GuardPort)
    assert isinstance(decorator.transformer, ImplicitReturnPort)

  def test_implicit_return_receives_the_transformer_port(self) -> None:
    assert isinstance(implicit_return().transformer, ImplicitReturnPort)

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

  def test_supplying_every_port_discovers_nothing(self) -> None:
    def double(x: int) -> int:
      return x * 2

    def identity(x: int) -> int:
      return x

    guarded = guarded_expression(runtime=PassthroughRuntime(), transformer=RecordingTransformer())
    plain = implicit_return(transformer=RecordingTransformer())

    assert guarded(double)(2) == 4
    assert plain(identity)(2) == 2
    assert 'modgud' not in Idunn().describe()

  def test_supplying_one_port_of_two_still_discovers_the_other(self) -> None:
    decorator = guarded_expression(transformer=RecordingTransformer())

    assert isinstance(decorator.runtime, GuardPort)
    assert 'GuardAdapter' in Idunn().describe()
