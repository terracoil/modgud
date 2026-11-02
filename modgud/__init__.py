"""Modgud: guard clauses and implicit returns for Python 3.11+.

Import everything you need from here::

  from modgud import CommonGuards, GuardFailureEnum, guarded_expression

The names in ``__all__`` are the supported public API. ``GuardRuntimePort`` and
``ImplicitReturnTransformerPort`` are the integration seam for the decorators'
``runtime=`` / ``transformer=`` parameters. Leaf packages remain importable, but
their layout may change between releases. Examples:
https://github.com/terracoil/modgud/tree/main/examples
"""

from importlib.metadata import PackageNotFoundError, version

from modgud.app import guarded_expression, implicit_return
from modgud.domain.guarded_expr import GuardClauseError, GuardFailureEnum, GuardFunction
from modgud.domain.guarded_expr.ports import GuardRuntimePort
from modgud.domain.implicit_ret import (
  ExplicitReturnDisallowedError,
  ImplicitReturnError,
  MissingImplicitReturnError,
  UnsupportedConstructError,
)
from modgud.domain.implicit_ret.ports import ImplicitReturnTransformerPort
from modgud.infrastructure import CommonGuards, GuardRegistry

try:
  __version__: str = version('modgud')  # single-sourced from pyproject.toml
except PackageNotFoundError:  # running from a checkout that was never installed
  __version__ = '0.0.0+uninstalled'

__all__ = [
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
]
