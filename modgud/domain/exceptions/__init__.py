"""
Domain exceptions package for modgud.

All exception classes used throughout the modgud library are defined here
following domain-driven design principles. The domain layer is passive
and contains no business logic - only exception class definitions.
"""

from .dependency_injection_error import DependencyInjectionError
from .explicit_return_disallowed_error import ExplicitReturnDisallowedError
from .guard_clause_error import GuardClauseError
from .implicit_return_error import ImplicitReturnError
from .missing_implicit_return_error import MissingImplicitReturnError
from .service_not_found_error import ServiceNotFoundError
from .unsupported_construct_error import UnsupportedConstructError

__all__ = [
  'GuardClauseError',
  'ImplicitReturnError',
  'ExplicitReturnDisallowedError',
  'MissingImplicitReturnError',
  'UnsupportedConstructError',
  'DependencyInjectionError',
  'ServiceNotFoundError',
]
