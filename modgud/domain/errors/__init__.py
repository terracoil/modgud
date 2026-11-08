"""Domain exceptions.

``GuardClauseError`` reports a guard failure. ``ImplicitReturnError`` is the common base of
everything the implicit-return AST rewrite raises; its subclasses identify the failure mode.
``MarkerNotRewrittenError`` is the one call-time error: an ``eop_`` form ran without a decorator.
"""

from .explicit_return_disallowed_error import ExplicitReturnDisallowedError
from .guard_clause_error import GuardClauseError
from .implicit_return_error import ImplicitReturnError
from .marker_not_rewritten_error import MarkerNotRewrittenError
from .marker_placement_error import MarkerPlacementError
from .marker_usage_error import MarkerUsageError
from .missing_implicit_return_error import MissingImplicitReturnError
from .unsupported_construct_error import UnsupportedConstructError

__all__ = [
  'ExplicitReturnDisallowedError',
  'GuardClauseError',
  'ImplicitReturnError',
  'MarkerNotRewrittenError',
  'MarkerPlacementError',
  'MarkerUsageError',
  'MissingImplicitReturnError',
  'UnsupportedConstructError',
]
