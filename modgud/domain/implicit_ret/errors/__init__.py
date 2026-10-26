"""Implicit-return transformation exceptions.

All errors raised by the implicit-return AST rewrite. `ImplicitReturnError`
is the common base; the three subclasses identify the specific failure mode.
"""

from .explicit_return_disallowed_error import ExplicitReturnDisallowedError
from .implicit_return_error import ImplicitReturnError
from .missing_implicit_return_error import MissingImplicitReturnError
from .unsupported_construct_error import UnsupportedConstructError

__all__ = [
  'ExplicitReturnDisallowedError',
  'ImplicitReturnError',
  'MissingImplicitReturnError',
  'UnsupportedConstructError',
]
