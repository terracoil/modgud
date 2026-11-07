"""Idunn wiring: discovery on first use, injection of the two ports, singletons, reset, fakes."""

from __future__ import annotations

import ast
from collections.abc import Iterator, Mapping
from typing import Any, Callable, NoReturn, TypeVar

import pytest
from idunn import Idunn
from modgud import (
  EopPort,
  GuardClauseError,
  GuardPort,
  ImplicitReturnPort,
  MarkerNotRewrittenError,
  eop_case,
  eop_cond,
  eop_match,
  guarded_expression,
  implicit_return,
)

F = TypeVar('F', bound=Callable[..., Any])


class PassthroughRuntime:
  """Guard-port fake: wraps nothing, so the decorated function is the one it was handed."""

  def transform(
    self,
    func: Callable[..., Any],
    continuance: int,
    imp_return_port: ImplicitReturnPort,
    implicit_return: bool,
    guards: tuple[Any, ...],
    strategy: Any,
    on_failure: Any,
    forms: Mapping[Any, EopPort],
  ) -> Callable[..., Any]:
    """Hand ``func`` back unguarded; the transformer still sees it when the rewrite is on."""
    return imp_return_port.transform_function(func, forms=forms) if implicit_return else func


class RecordingTransformer:
  """Implicit-return fake: records each function it is asked to transform and returns it as-is."""

  def __init__(self) -> None:
    """Start with nothing recorded."""
    self.seen: list[Callable[..., Any]] = []

  def transform(self, func: F, *, forms: Mapping[Any, EopPort]) -> F:
    """Record ``func`` and hand it back unchanged."""
    self.seen.append(func)
    return func

  def transform_function(
    self, func: Callable[..., Any], *, forms: Mapping[Any, EopPort], implicit_return: bool = True
  ) -> Callable[..., Any]:
    """Record ``func`` and hand it back unchanged."""
    self.seen.append(func)
    return func


class RefusingForm:
  """Form-port fake: lowers nothing and refuses with a recognisable message."""

  def lower(
    self, call: ast.Call, *, hoistable: bool, fresh: Callable[[str], str]
  ) -> tuple[list[ast.stmt], ast.expr]:
    """Hand the call back untouched."""
    return [], call

  def refuse(self) -> NoReturn:
    """Refuse with a message the tests can spot."""
    raise MarkerNotRewrittenError('fake form')


def every_port() -> dict[str, Any]:
  """Return the five ports a decoration can supply, as fakes."""
  return {
    'guard_port': PassthroughRuntime(),
    'imp_return_port': RecordingTransformer(),
    'eop_cond_port': RefusingForm(),
    'eop_case_port': RefusingForm(),
    'eop_match_port': RefusingForm(),
  }


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

  def test_the_first_decoration_discovers_every_adapter_and_port(self) -> None:
    guarded_expression()
    report = Idunn().bootstrap('modgud')  # a cache hit: the decoration already discovered

    assert report['root_package'] == 'modgud'
    assert set(report['registered_adapters']) == {
      'modgud.infrastructure.adapters.eop_case_adapter.EopCaseAdapter',
      'modgud.infrastructure.adapters.eop_cond_adapter.EopCondAdapter',
      'modgud.infrastructure.adapters.eop_match_adapter.EopMatchAdapter',
      'modgud.infrastructure.adapters.guard_adapter.GuardAdapter',
      'modgud.infrastructure.adapters.implicit_return_adapter.ImplicitReturnAdapter',
    }
    assert set(report['registered_ports']) == {
      'modgud.domain.ports.eop_port.EopPort',
      'modgud.domain.ports.guard_port.GuardPort',
      'modgud.domain.ports.implicit_return_port.ImplicitReturnPort',
    }

  def test_a_marker_called_outside_a_decorator_discovers_and_refuses(self) -> None:
    with pytest.raises(MarkerNotRewrittenError, match='eop_cond only works inside'):
      eop_cond(default=None)

    assert 'EopCondAdapter' in Idunn().describe()

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

  def test_guarded_expression_receives_every_port(self) -> None:
    decorator = guarded_expression()

    assert isinstance(decorator.guard_port, GuardPort)
    assert isinstance(decorator.imp_return_port, ImplicitReturnPort)
    assert isinstance(decorator.eop_cond_port, EopPort)
    assert isinstance(decorator.eop_case_port, EopPort)
    assert isinstance(decorator.eop_match_port, EopPort)

  def test_each_form_port_is_the_adapter_for_its_key(self) -> None:
    decorator = guarded_expression()

    assert type(decorator.eop_cond_port).__name__ == 'EopCondAdapter'
    assert type(decorator.eop_case_port).__name__ == 'EopCaseAdapter'
    assert type(decorator.eop_match_port).__name__ == 'EopMatchAdapter'
    assert implicit_return().eop_case_port is decorator.eop_case_port

  def test_implicit_return_receives_the_transformer_port(self) -> None:
    assert isinstance(implicit_return().imp_return_port, ImplicitReturnPort)

  def test_adapters_are_singletons_shared_across_decorators(self) -> None:
    first, second = guarded_expression(), guarded_expression()

    assert first.guard_port is second.guard_port
    assert first.imp_return_port is second.imp_return_port
    assert implicit_return().imp_return_port is first.imp_return_port


class TestReset:
  """``Idunn().reset()`` forgets the wiring; the next decoration re-discovers it."""

  def test_decoration_still_works_after_reset(self) -> None:
    before = guarded_expression().guard_port
    Idunn().reset(environment=Idunn().environment)

    @guarded_expression(lambda x: x > 0 or 'x must be positive', implicit_return=False)
    def double(x: int) -> int:
      return x * 2

    assert double(2) == 4
    with pytest.raises(GuardClauseError, match='x must be positive'):
      double(-1)
    assert guarded_expression().guard_port is not before


class TestFakeSeam:
  """A caller-supplied port implementation wins over the injected adapter."""

  def test_guarded_expression_uses_a_supplied_transformer(self) -> None:
    fake = RecordingTransformer()

    def triple(x: int) -> int:
      return x * 3

    decorated = guarded_expression(imp_return_port=fake)(triple)

    assert fake.seen == [triple]
    assert decorated(2) == 6

  def test_implicit_return_uses_a_supplied_transformer(self) -> None:
    fake = RecordingTransformer()

    def identity(x: int) -> int:
      return x

    decorated = implicit_return(imp_return_port=fake)(identity)

    assert fake.seen == [identity]
    assert decorated is identity

  def test_supplying_every_port_discovers_nothing(self) -> None:
    def double(x: int) -> int:
      return x * 2

    def identity(x: int) -> int:
      return x

    guarded = guarded_expression(**every_port())
    ports = every_port()
    del ports['guard_port']
    plain = implicit_return(**ports)

    assert guarded(double)(2) == 4
    assert plain(identity)(2) == 2
    assert 'modgud' not in Idunn().describe()

  def test_supplying_some_ports_still_discovers_the_others(self) -> None:
    decorator = guarded_expression(imp_return_port=RecordingTransformer())

    assert isinstance(decorator.guard_port, GuardPort)
    assert 'GuardAdapter' in Idunn().describe()
    assert 'EopMatchAdapter' in Idunn().describe()

  def test_a_supplied_form_port_handles_the_un_rewritten_call(self) -> None:
    with pytest.raises(MarkerNotRewrittenError, match='fake form'):
      eop_case._refuse(port=RefusingForm())
    with pytest.raises(MarkerNotRewrittenError, match='fake form'):
      eop_match._refuse(port=RefusingForm())
    assert 'modgud' not in Idunn().describe()
