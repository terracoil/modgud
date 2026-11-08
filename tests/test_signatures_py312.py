"""PEP 695 part of the signature regression suite (Python 3.12+ only).

Same comparisons as ``tests/test_signatures.py``, plus ``__type_params__``: the rewrite
rebuilds the function with ``types.FunctionType``, which starts with no type parameters, so
they must be copied from the original. ``tests/conftest.py`` skips this file on 3.11.
"""

import inspect
import sys
from typing import Any, Callable

import pytest

# conftest's collect_ignore covers directory runs; a path named on the command line bypasses
# it, so skip here, before importing a module that 3.11 cannot parse.
if sys.version_info < (3, 12):
  pytest.skip('PEP 695 syntax needs Python 3.12+', allow_module_level=True)

from tests import signature_fixtures_py312 as fx  # noqa: E402

Fn = Callable[..., Any]
CASES: list[Any] = [
  pytest.param(fx.identity, fx.identity_twin, 'identity', id='guarded-implicit'),
  pytest.param(fx.pair, fx.pair_twin, 'pair', id='implicit-every-param-kind'),
  pytest.param(fx.first, fx.first_twin, 'first', id='guarded-explicit'),
  pytest.param(fx.own_type_param, fx.own_type_param_twin, 'own_type_param', id='body-names-T'),
  pytest.param(fx.Box.get, fx.Box.get_twin, 'Box.get', id='generic-class-method'),
]
CASE_ARGS: str = 'decorated, twin, qualname'


class TestTypeParamSignatures:
  """Decorated PEP 695 functions report the same metadata as their undecorated twins."""

  @staticmethod
  def describe(param: Any) -> tuple[Any, ...]:
    """Everything that identifies a type parameter except its object identity."""
    return (
      type(param),
      param.__name__,
      getattr(param, '__bound__', None),
      getattr(param, '__constraints__', ()),
    )

  @staticmethod
  def printed(annotations: dict[str, Any]) -> dict[str, str]:
    """Annotations with each value replaced by its printed form."""
    return {name: str(value) for name, value in annotations.items()}

  @pytest.mark.parametrize(CASE_ARGS, CASES)
  def test_signature_matches_twin(self, decorated: Fn, twin: Fn, qualname: str) -> None:
    assert str(inspect.signature(decorated)) == str(inspect.signature(twin))

  @pytest.mark.parametrize(CASE_ARGS, CASES)
  def test_type_params_match_twin(self, decorated: Fn, twin: Fn, qualname: str) -> None:
    actual: list[tuple[Any, ...]] = [self.describe(p) for p in decorated.__type_params__]
    assert actual == [self.describe(p) for p in twin.__type_params__]
    assert inspect.unwrap(decorated).__type_params__ == decorated.__type_params__

  @pytest.mark.parametrize(CASE_ARGS, CASES)
  def test_type_params_are_the_ones_in_the_annotations(
    self, decorated: Fn, twin: Fn, qualname: str
  ) -> None:
    """The copied parameters are the original objects, not look-alikes from the re-compile."""
    annotated: list[Any] = list(decorated.__annotations__.values())
    first: Any = decorated.__type_params__[0]
    assert any(first is a or first in getattr(a, '__args__', ()) for a in annotated)

  @pytest.mark.parametrize(CASE_ARGS, CASES)
  def test_annotations_and_defaults_match_twin(
    self, decorated: Fn, twin: Fn, qualname: str
  ) -> None:
    """Annotations compare by printed form: the twin owns distinct TypeVars of the same name."""
    assert self.printed(decorated.__annotations__) == self.printed(twin.__annotations__)
    assert inspect.unwrap(decorated).__defaults__ == twin.__defaults__
    assert inspect.unwrap(decorated).__kwdefaults__ == twin.__kwdefaults__

  @pytest.mark.parametrize(CASE_ARGS, CASES)
  def test_name_qualname_and_doc_preserved(self, decorated: Fn, twin: Fn, qualname: str) -> None:
    assert decorated.__name__ == qualname.rsplit('.', 1)[-1]
    assert decorated.__qualname__ == qualname
    assert decorated.__doc__ is not None
    assert decorated.__doc__ == twin.__doc__


class TestTypeParamBehaviour:
  """Calls work and the body sees the same type parameters the signature advertises."""

  def test_calls_match_twins(self) -> None:
    assert fx.identity(5) == fx.identity_twin(5)
    assert fx.pair('k', 1, 'extra') == fx.pair_twin('k', 1, 'extra')
    assert fx.first([]) is None
    assert fx.Box(None).get(3) == fx.Box(None).get_twin(3)

  def test_body_sees_the_advertised_type_param(self) -> None:
    assert fx.own_type_param_twin(1) is fx.own_type_param_twin.__type_params__[0]
    assert fx.own_type_param(1) is fx.own_type_param.__type_params__[0]

  def test_method_body_sees_class_type_param(self) -> None:
    assert fx.Box(1).item_type_twin() is fx.Box.__type_params__[0]
    assert fx.Box(1).item_type() is fx.Box.__type_params__[0]
