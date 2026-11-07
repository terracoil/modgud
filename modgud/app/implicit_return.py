"""Standalone implicit_return decorator.

Ruby-style implicit returns: the last expression in each branch is the
function's return value. Explicit `return` statements are not allowed.
Apply it with parentheses: ``@implicit_return()``.
"""

from __future__ import annotations

from idunn import Invert

from modgud.domain.enums import EopFormEnum
from modgud.domain.ports import EopPort, ImplicitReturnPort
from modgud.domain.types import F


class implicit_return:
  """Transform a function to use implicit returns.

  ``imp_return_port`` and the three ``eop_*_port`` ports are injected by Idunn, which discovers
  modgud's adapters the first time a decoration leaves one of them to injection. Pass a port
  explicitly to substitute a different implementation (e.g. a test fake); pass all four and
  nothing is discovered.

  :raises ExplicitReturnDisallowedError: if explicit return statements are found.
  :raises MissingImplicitReturnError: if a code path doesn't yield a value.
  :raises UnsupportedConstructError: if an unsupported construct is at tail position.
  :raises MarkerUsageError: if an ``eop_`` form is malformed.
  :raises MarkerPlacementError: if an ``eop_`` form sits where it cannot be lowered.
  :raises ValueError: if the function source cannot be extracted.
  :raises TypeError: if applied above ``@guarded_expression``, whose guards the rewrite would drop.
  """

  imp_return_port: ImplicitReturnPort  # assigned by @Invert
  eop_cond_port: EopPort  # assigned by @Invert
  eop_case_port: EopPort  # assigned by @Invert
  eop_match_port: EopPort  # assigned by @Invert

  # @Invert assigns the port parameters to self before the body runs.
  # noinspection PyUnusedLocal
  @Invert(
    bootstrap='modgud',
    keys={
      'eop_cond_port': EopFormEnum.COND,
      'eop_case_port': EopFormEnum.CASE,
      'eop_match_port': EopFormEnum.MATCH,
    },
  )
  def __init__(
    self,
    *,
    imp_return_port: ImplicitReturnPort,
    eop_cond_port: EopPort,
    eop_case_port: EopPort,
    eop_match_port: EopPort,
  ) -> None:
    """Receive the implicit-return port and the three form ports from Idunn, or from the caller."""

  def __call__(self, func: F) -> F:
    """Hand ``func`` to the implicit-return port, which rewrites it and lowers every form."""
    return self.imp_return_port.transform(func, forms=self._forms())

  def _forms(self) -> dict[EopFormEnum, EopPort]:
    """Map each form to the port that lowers it."""
    return {
      EopFormEnum.COND: self.eop_cond_port,
      EopFormEnum.CASE: self.eop_case_port,
      EopFormEnum.MATCH: self.eop_match_port,
    }
