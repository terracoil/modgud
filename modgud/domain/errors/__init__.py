"""Domain exceptions.

``GuardClauseError`` reports a guard failure. ``ImplicitReturnError`` is the common base of
everything the implicit-return AST rewrite raises; its three subclasses identify the failure mode.
"""

from .explicit_return_disallowed_error import ExplicitReturnDisallowedError
from .guard_clause_error import GuardClauseError
from .implicit_return_error import ImplicitReturnError
from .missing_implicit_return_error import MissingImplicitReturnError
from .unsupported_construct_error import UnsupportedConstructError

__all__ = [
  'ExplicitReturnDisallowedError',
  'GuardClauseError',
  'ImplicitReturnError',
  'MissingImplicitReturnError',
  'UnsupportedConstructError',
]
