"""Idunn adapters: the concrete implementations of modgud's ports.

Idunn discovers these the first time an app decorator needs a port, through
``@Invert(bootstrap='modgud')``, and injects them. The three form adapters share ``EopPort``
and are told apart by their ``EopFormEnum`` key. Nothing outside this package and its unit
tests imports them.
"""

from .eop_case_adapter import EopCaseAdapter
from .eop_cond_adapter import EopCondAdapter
from .eop_match_adapter import EopMatchAdapter
from .guard_adapter import GuardAdapter
from .implicit_return_adapter import ImplicitReturnAdapter

__all__ = [
  'EopCaseAdapter',
  'EopCondAdapter',
  'EopMatchAdapter',
  'GuardAdapter',
  'ImplicitReturnAdapter',
]
