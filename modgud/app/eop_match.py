"""``eop_match``: Elixir's ``match?`` as an expression, lowered by the implicit-return rewrite."""

from __future__ import annotations

from typing import Final, NoReturn

from idunn import Invert

from modgud.domain.enums import EopFormEnum
from modgud.domain.ports import EopPort


class EopMatch:
  """Typed stand-in for ``eop_match``; the rewrite replaces every call inside a decorated function."""

  __modgud_eop_form__: Final[EopFormEnum] = EopFormEnum.MATCH

  def __call__(self, pattern: object, value: object) -> bool:
    """Return whether ``value`` matches ``pattern``, as in Elixir's ``match?/2``.
    ``pattern`` may be ``eop_when(pattern, guard)``; captures are usable only inside that guard.
    """
    self._refuse()

  @staticmethod
  @Invert(bootstrap='modgud', keys={'port': EopFormEnum.MATCH})
  def _refuse(*, port: EopPort) -> NoReturn:
    """Delegate the refusal of an un-rewritten call to the injected adapter."""
    port.refuse()


eop_match: Final[EopMatch] = EopMatch()
