"""Modgud: guard clauses and implicit returns for Python 3.11+.

Import everything you need from here::

  from modgud import CommonGuards, GuardFailureEnum, guarded_expression

The names in ``__all__`` are the supported public API. ``GuardPort`` and
``ImplicitReturnPort`` are the integration seam for the decorators'
``runtime=`` / ``transformer=`` parameters. Leaf packages remain importable, but
their layout may change between releases. Examples:
https://github.com/terracoil/modgud/tree/main/examples
"""

from importlib.metadata import PackageNotFoundError, version

from modgud.app import CommonGuards, GuardRegistry, guarded_expression, implicit_return
from modgud.domain.enums import GuardFailureEnum
from modgud.domain.errors import (
  ExplicitReturnDisallowedError,
  GuardClauseError,
  ImplicitReturnError,
  MissingImplicitReturnError,
  UnsupportedConstructError,
)
from modgud.domain.ports import GuardPort, ImplicitReturnPort
from modgud.domain.types import GuardFunction

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
  'GuardPort',
  'ImplicitReturnError',
  'ImplicitReturnPort',
  'MissingImplicitReturnError',
  'UnsupportedConstructError',
  'guarded_expression',
  'implicit_return',
]
