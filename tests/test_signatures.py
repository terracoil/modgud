"""Signature regression suite: decorating a function must not change what ``inspect`` sees.

The implicit-return rewrite re-compiles the function (defaults and annotations are stripped
from the tree and reused from the original) and the guard runtime wraps the result with
``functools.wraps``. Every signature feature is a chance to lose something silently, so each
case pairs a decorated fixture with an undecorated twin from ``tests/signature_fixtures.py``.

``__defaults__`` / ``__kwdefaults__`` are read from ``inspect.unwrap(decorated)``, the function
that actually runs: ``functools.wraps`` does not copy them onto a ``(*args, **kwargs)``
wrapper, and ``inspect.signature`` follows ``__wrapped__`` to find them.
"""

import asyncio
import inspect
from typing import Any, Callable

import pytest

from tests import signature_fixtures as fx

# (decorated, twin, expected __qualname__, call args, call kwargs); the call omits defaults.
CASES: list[Any] = [
  pytest.param(fx.posonly, fx.posonly_twin, 'posonly', (1,), {}, id='positional-only'),
  pytest.param(fx.kwonly, fx.kwonly_twin, 'kwonly', (1,), {'m': 'ab'}, id='keyword-only'),
  pytest.param(fx.star_args, fx.star_args_twin, 'star_args', (1, 2), {'x': 'y'}, id='star-args'),
  pytest.param(
    fx.module_default, fx.module_default_twin, 'module_default', (4,), {}, id='module-default'
  ),
  pytest.param(fx.stacked, fx.stacked_twin, 'stacked', (2,), {}, id='stacked-guards'),
  pytest.param(fx.layered, fx.layered_twin, 'layered', (7,), {}, id='guard-over-implicit'),
  pytest.param(fx.fetch, fx.fetch_twin, 'fetch', (9,), {}, id='async-guarded'),
  pytest.param(fx.fetch_plain, fx.fetch_plain_twin, 'fetch_plain', (2,), {}, id='async-implicit'),
  pytest.param(
    fx.Pricing.total,
    fx.Pricing.total_twin,
    'Pricing.total',
    (fx.Pricing(), 3),
    {},
    id='method-class-default',
  ),
  pytest.param(
    fx.Pricing().total,
    fx.Pricing().total_twin,
    'Pricing.total',
    (30,),
    {},
    id='bound-method-class-default',
  ),
  pytest.param(
    fx.Pricing.scaled,
    fx.Pricing.scaled_twin,
    'Pricing.scaled',
    (4,),
    {},
    id='classmethod-class-default',
  ),
]
CASE_ARGS: str = 'decorated, twin, qualname, args, kwargs'
Fn = Callable[..., Any]


class TestSignaturePreservation:
  """Each decorated fixture reports the same signature metadata as its undecorated twin."""

  @staticmethod
  def call(fn: Fn, args: tuple[Any, ...], kwargs: dict[str, Any]) -> Any:
    """Call ``fn``, driving the coroutine to completion when it is async."""
    outcome: Any = fn(*args, **kwargs)
    return asyncio.run(outcome) if inspect.iscoroutine(outcome) else outcome

  @pytest.mark.parametrize(CASE_ARGS, CASES)
  def test_signature_text_matches_twin(
    self, decorated: Fn, twin: Fn, qualname: str, args: tuple[Any, ...], kwargs: dict[str, Any]
  ) -> None:
    assert str(inspect.signature(decorated)) == str(inspect.signature(twin))

  @pytest.mark.parametrize(CASE_ARGS, CASES)
  def test_signature_parameters_match_twin(
    self, decorated: Fn, twin: Fn, qualname: str, args: tuple[Any, ...], kwargs: dict[str, Any]
  ) -> None:
    """Kinds, defaults and annotations, compared as objects rather than as text."""
    actual: inspect.Signature = inspect.signature(decorated)
    expected: inspect.Signature = inspect.signature(twin)
    assert list(actual.parameters.values()) == list(expected.parameters.values())
    assert actual.return_annotation == expected.return_annotation

  @pytest.mark.parametrize(CASE_ARGS, CASES)
  def test_annotations_match_twin(
    self, decorated: Fn, twin: Fn, qualname: str, args: tuple[Any, ...], kwargs: dict[str, Any]
  ) -> None:
    assert decorated.__annotations__ == twin.__annotations__
    assert inspect.unwrap(decorated).__annotations__ == twin.__annotations__

  @pytest.mark.parametrize(CASE_ARGS, CASES)
  def test_defaults_match_twin(
    self, decorated: Fn, twin: Fn, qualname: str, args: tuple[Any, ...], kwargs: dict[str, Any]
  ) -> None:
    runs: Fn = inspect.unwrap(decorated)
    assert runs.__defaults__ == twin.__defaults__
    assert runs.__kwdefaults__ == twin.__kwdefaults__

  @pytest.mark.parametrize(CASE_ARGS, CASES)
  def test_name_qualname_and_doc_preserved(
    self, decorated: Fn, twin: Fn, qualname: str, args: tuple[Any, ...], kwargs: dict[str, Any]
  ) -> None:
    assert decorated.__name__ == qualname.rsplit('.', 1)[-1]
    assert decorated.__qualname__ == qualname
    assert decorated.__module__ == twin.__module__
    assert decorated.__doc__ is not None
    assert decorated.__doc__ == twin.__doc__

  @pytest.mark.parametrize(CASE_ARGS, CASES)
  def test_coroutine_flag_matches_twin(
    self, decorated: Fn, twin: Fn, qualname: str, args: tuple[Any, ...], kwargs: dict[str, Any]
  ) -> None:
    assert inspect.iscoroutinefunction(decorated) == inspect.iscoroutinefunction(twin)

  @pytest.mark.parametrize(CASE_ARGS, CASES)
  def test_call_with_defaults_matches_twin(
    self, decorated: Fn, twin: Fn, qualname: str, args: tuple[Any, ...], kwargs: dict[str, Any]
  ) -> None:
    """The defaults are not just reported but used: the call leaves them all out."""
    assert self.call(decorated, args, kwargs) == self.call(twin, args, kwargs)


class TestDefaultIdentity:
  """Defaults are the original objects, not re-evaluated copies."""

  def test_module_global_default_is_the_same_object(self) -> None:
    assert inspect.unwrap(fx.module_default).__defaults__ == (fx.DEFAULT_LIMIT, fx.SENTINEL)
    assert inspect.unwrap(fx.module_default).__defaults__[1] is fx.SENTINEL
    assert fx.module_default(1) is True

  def test_class_attribute_defaults_resolve_to_class_values(self) -> None:
    assert fx.Pricing.total.__defaults__ is None  # the guard wrapper itself has none
    assert inspect.unwrap(fx.Pricing.total).__defaults__ == (fx.Pricing.rate,)
    assert inspect.unwrap(fx.Pricing.total).__kwdefaults__ == {'cap': fx.Pricing.cap}
    assert fx.Pricing().total(30) == fx.Pricing.cap


class TestBindingFollowsSignature:
  """The re-compiled code enforces the same parameter kinds, not just the same metadata."""

  def test_positional_only_rejects_keyword(self) -> None:
    with pytest.raises(TypeError, match='positional-only'):
      fx.posonly(a=1)

  def test_keyword_only_rejects_positional(self) -> None:
    with pytest.raises(TypeError, match='positional argument'):
      fx.kwonly(1, 3, 'ab')

  def test_required_keyword_only_is_still_required(self) -> None:
    with pytest.raises(TypeError, match='keyword-only'):
      fx.kwonly(1)

  def test_stacked_positional_only_rejects_keyword(self) -> None:
    with pytest.raises(TypeError, match='positional-only'):
      fx.stacked(2, scale=2.0, a=1)
