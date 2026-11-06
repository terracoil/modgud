"""Implicit-return domain: errors, ports."""

from .errors import (
  ExplicitReturnDisallowedError,
  ImplicitReturnError,
  MissingImplicitReturnError,
  UnsupportedConstructError,
)
from .ports import ImplicitReturnPort

__all__ = [
  'ExplicitReturnDisallowedError',
  'ImplicitReturnError',
  'ImplicitReturnPort',
  'MissingImplicitReturnError',
  'UnsupportedConstructError',
]
