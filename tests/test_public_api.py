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
import modgud.domain.enums
import modgud.domain.errors
import modgud.domain.ports
import modgud.domain.types
import modgud.infrastructure

REPO_ROOT = Path(__file__).resolve().parent.parent
PUBLIC_NAMES = {
  'CommonGuards',
  'EopPort',
  'ExplicitReturnDisallowedError',
  'GuardClauseError',
  'GuardFailureEnum',
  'GuardFunction',
  'GuardRegistry',
  'GuardPort',
  'ImplicitReturnError',
  'ImplicitReturnPort',
  'MarkerNotRewrittenError',
  'MarkerPlacementError',
  'MarkerUsageError',
  'MissingImplicitReturnError',
  'UnsupportedConstructError',
  'eop_case',
  'eop_clause',
  'eop_cond',
  'eop_match',
  'eop_var',
  'eop_when',
  'guarded_expression',
  'implicit_return',
}
DOMAIN_NAMES = {
  'EopPort',
  'ExplicitReturnDisallowedError',
  'GuardClauseError',
  'GuardFailureEnum',
  'GuardFunction',
  'GuardPort',
  'ImplicitReturnError',
  'ImplicitReturnPort',
  'MarkerNotRewrittenError',
  'MarkerPlacementError',
  'MarkerUsageError',
  'MissingImplicitReturnError',
  'UnsupportedConstructError',
  'eop_clause',
}
APP_NAMES = {
  'CommonGuards',
  'GuardRegistry',
  'eop_case',
  'eop_cond',
  'eop_match',
  'eop_var',
  'eop_when',
  'guarded_expression',
  'implicit_return',
}
INTERNAL_NAMES = {
  'EopCaseAdapter',
  'EopCondAdapter',
  'EopMatchAdapter',
  'GuardAdapter',
  'ImplicitReturnAdapter',
  'NoExplicitReturnChecker',
  'TailRewriter',
  'TopLevelTransformer',
}


class TestFacadeExports:
  def test_root_facade_exports_exactly_the_public_names(self) -> None:
    assert len(modgud.__all__) == len(set(modgud.__all__))
    assert set(modgud.__all__) == PUBLIC_NAMES

  def test_domain_facade_exports_the_passive_types_and_ports(self) -> None:
    assert set(modgud.domain.__all__) == DOMAIN_NAMES

  def test_infrastructure_facade_exports_nothing(self) -> None:
    assert modgud.infrastructure.__all__ == []

  def test_app_package_exports_the_decorators_and_the_guard_toolkit(self) -> None:
    assert set(modgud.app.__all__) == APP_NAMES

  def test_internals_are_not_exported_by_any_facade(self) -> None:
    for facade in (modgud, modgud.app, modgud.domain):
      assert not INTERNAL_NAMES & set(facade.__all__)


class TestVersion:
  def test_version_is_single_sourced(self) -> None:
    assert modgud.__version__ == importlib.metadata.version('modgud') == '2.0.0'


class TestFacadeIdentity:
  def test_root_names_are_the_leaf_objects(self) -> None:
    leaves = {
      'guarded_expression': modgud.app.guarded_expression,
      'implicit_return': modgud.app.implicit_return,
      'GuardFailureEnum': modgud.domain.enums.GuardFailureEnum,
      'GuardClauseError': modgud.domain.errors.GuardClauseError,
      'GuardFunction': modgud.domain.types.GuardFunction,
      'GuardPort': modgud.domain.ports.GuardPort,
      'ImplicitReturnError': modgud.domain.errors.ImplicitReturnError,
      'ExplicitReturnDisallowedError': modgud.domain.errors.ExplicitReturnDisallowedError,
      'MissingImplicitReturnError': modgud.domain.errors.MissingImplicitReturnError,
      'UnsupportedConstructError': modgud.domain.errors.UnsupportedConstructError,
      'ImplicitReturnPort': modgud.domain.ports.ImplicitReturnPort,
      'CommonGuards': modgud.app.CommonGuards,
      'GuardRegistry': modgud.app.GuardRegistry,
      'EopPort': modgud.domain.ports.EopPort,
      'MarkerNotRewrittenError': modgud.domain.errors.MarkerNotRewrittenError,
      'MarkerPlacementError': modgud.domain.errors.MarkerPlacementError,
      'MarkerUsageError': modgud.domain.errors.MarkerUsageError,
      'eop_case': modgud.app.eop_case,
      'eop_clause': modgud.domain.types.eop_clause,
      'eop_cond': modgud.app.eop_cond,
      'eop_match': modgud.app.eop_match,
      'eop_var': modgud.app.eop_var,
      'eop_when': modgud.app.eop_when,
    }
    assert set(leaves) == PUBLIC_NAMES
    for name, leaf in leaves.items():
      assert getattr(modgud, name) is leaf, name

  def test_domain_names_are_the_root_objects(self) -> None:
    for name in DOMAIN_NAMES:
      assert getattr(modgud.domain, name) is getattr(modgud, name), name


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
