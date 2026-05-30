"""Implicit-return domain: errors, ports."""

from .errors import (
  ExplicitReturnDisallowedError,
  ImplicitReturnError,
  MissingImplicitReturnError,
  UnsupportedConstructError,
)

__all__ = [
  'ExplicitReturnDisallowedError',
  'ImplicitReturnError',
  'MissingImplicitReturnError',
  'UnsupportedConstructError',
]
