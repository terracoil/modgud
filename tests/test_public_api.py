"""Public-API tests: the three facades export exactly what they promise, and nothing more."""

from __future__ import annotations

import importlib.metadata
import subprocess
import sys
import textwrap
from pathlib import Path

import modgud
import modgud.app
import modgud.domain
import modgud.domain.guarded_expr
import modgud.domain.guarded_expr.ports
import modgud.domain.implicit_ret
import modgud.domain.implicit_ret.ports
import modgud.infrastructure
import modgud.infrastructure.common

REPO_ROOT = Path(__file__).resolve().parent.parent
PUBLIC_NAMES = {
  'CommonGuards',
  'ExplicitReturnDisallowedError',
  'GuardClauseError',
  'GuardFailureEnum',
  'GuardFunction',
  'GuardRegistry',
  'GuardRuntimePort',
  'ImplicitReturnError',
  'ImplicitReturnTransformerPort',
  'MissingImplicitReturnError',
  'UnsupportedConstructError',
  'guarded_expression',
  'implicit_return',
}
DOMAIN_NAMES = {
  'ExplicitReturnDisallowedError',
  'GuardClauseError',
  'GuardFailureEnum',
  'GuardFunction',
  'ImplicitReturnError',
  'MissingImplicitReturnError',
  'UnsupportedConstructError',
}
INTERNAL_NAMES = {
  'GuardRuntime',
  'ImplicitReturnTransformer',
  'Wiring',
  'NoExplicitReturnChecker',
  'TailRewriter',
  'TopLevelTransformer',
}


class TestFacadeExports:
  def test_root_facade_exports_exactly_the_public_names(self) -> None:
    assert len(modgud.__all__) == len(set(modgud.__all__))
    assert set(modgud.__all__) == PUBLIC_NAMES

  def test_domain_facade_exports_the_passive_types(self) -> None:
    assert set(modgud.domain.__all__) == DOMAIN_NAMES

  def test_infrastructure_facade_exports_the_guard_toolkit(self) -> None:
    assert modgud.infrastructure.__all__ == ['CommonGuards', 'GuardRegistry']

  def test_wiring_is_reachable_from_the_app_package(self) -> None:
    assert 'Wiring' in modgud.app.__all__

  def test_internals_are_not_exported_by_any_facade(self) -> None:
    for facade in (modgud, modgud.domain, modgud.infrastructure):
      assert not INTERNAL_NAMES & set(facade.__all__)
    assert not {'GuardRuntimePort', 'ImplicitReturnTransformerPort'} & set(modgud.domain.__all__)


class TestVersion:
  def test_version_is_single_sourced(self) -> None:
    assert modgud.__version__ == importlib.metadata.version('modgud') == '2.0.0'


class TestFacadeIdentity:
  def test_root_names_are_the_leaf_objects(self) -> None:
    leaves = {
      'guarded_expression': modgud.app.guarded_expression,
      'implicit_return': modgud.app.implicit_return,
      'GuardFailureEnum': modgud.domain.guarded_expr.GuardFailureEnum,
      'GuardClauseError': modgud.domain.guarded_expr.GuardClauseError,
      'GuardFunction': modgud.domain.guarded_expr.GuardFunction,
      'GuardRuntimePort': modgud.domain.guarded_expr.ports.GuardRuntimePort,
      'ImplicitReturnError': modgud.domain.implicit_ret.ImplicitReturnError,
      'ExplicitReturnDisallowedError': modgud.domain.implicit_ret.ExplicitReturnDisallowedError,
      'MissingImplicitReturnError': modgud.domain.implicit_ret.MissingImplicitReturnError,
      'UnsupportedConstructError': modgud.domain.implicit_ret.UnsupportedConstructError,
      'ImplicitReturnTransformerPort': (
        modgud.domain.implicit_ret.ports.ImplicitReturnTransformerPort
      ),
      'CommonGuards': modgud.infrastructure.common.CommonGuards,
      'GuardRegistry': modgud.infrastructure.common.GuardRegistry,
    }
    assert set(leaves) == PUBLIC_NAMES
    for name, leaf in leaves.items():
      assert getattr(modgud, name) is leaf, name

  def test_domain_and_infrastructure_names_are_the_root_objects(self) -> None:
    for name in DOMAIN_NAMES:
      assert getattr(modgud.domain, name) is getattr(modgud, name), name
    for name in modgud.infrastructure.__all__:
      assert getattr(modgud.infrastructure, name) is getattr(modgud, name), name


class TestFreshProcess:
  def test_importing_modgud_does_not_load_the_adapters(self) -> None:
    code = 'import sys, modgud; assert "modgud.infrastructure.adapters" not in sys.modules'
    result = subprocess.run(
      [sys.executable, '-c', code], capture_output=True, text=True, timeout=60, cwd=REPO_ROOT
    )
    assert result.returncode == 0, result.stderr

  def test_a_fresh_process_can_decorate_and_fire_a_guard(self, tmp_path: Path) -> None:
    script = tmp_path / 'fresh.py'
    script.write_text(
      textwrap.dedent(
        """
        from modgud import CommonGuards, GuardClauseError, guarded_expression


        @guarded_expression(CommonGuards.positive('x'))
        def double(x: int) -> int:
          x * 2


        assert double(4) == 8
        try:
          double(-1)
        except GuardClauseError:
          pass
        else:
          raise AssertionError('guard did not fire')
        """
      ),
      encoding='utf-8',
    )
    result = subprocess.run(
      [sys.executable, str(script)], capture_output=True, text=True, timeout=60, cwd=REPO_ROOT
    )
    assert result.returncode == 0, result.stderr
