"""Modgud: guard clauses and implicit returns for Python 3.11+.

Import everything you need from here::

  from modgud import CommonGuards, GuardFailureEnum, guarded_expression

The names in ``__all__`` are the supported public API. ``GuardPort``,
``ImplicitReturnPort`` and ``EopPort`` are the integration seam for the decorators'
``guard_port=`` / ``imp_return_port=`` / ``eop_*_port=`` parameters. Leaf packages remain importable, but
their layout may change between releases. Examples:
https://github.com/terracoil/modgud/tree/main/examples
"""

from importlib.metadata import PackageNotFoundError, version

from modgud.app import (
  CommonGuards,
  GuardRegistry,
  eop_case,
  eop_cond,
  eop_match,
  eop_var,
  eop_when,
  guarded_expression,
  implicit_return,
)
from modgud.domain import (
  EopPort,
  ExplicitReturnDisallowedError,
  GuardClauseError,
  GuardFailureEnum,
  GuardFunction,
  GuardPort,
  ImplicitReturnError,
  ImplicitReturnPort,
  MarkerNotRewrittenError,
  MarkerPlacementError,
  MarkerUsageError,
  MissingImplicitReturnError,
  UnsupportedConstructError,
  eop_clause,
)

try:
  __version__: str = version('modgud')  # single-sourced from pyproject.toml
except PackageNotFoundError:  # running from a checkout that was never installed
  __version__ = '0.0.0+uninstalled'

__all__ = [
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
]
