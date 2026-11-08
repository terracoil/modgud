"""``eop_cond``: Elixir's ``cond`` as an expression, lowered by the implicit-return rewrite."""

from __future__ import annotations

from typing import Final, NoReturn, TypeVar

from idunn import Invert

from modgud.domain.enums import EopFormEnum
from modgud.domain.ports import EopPort
from modgud.domain.types import eop_clause

T = TypeVar('T')
D = TypeVar('D')


class EopCond:
  """Typed stand-in for ``eop_cond``; the rewrite replaces every call inside a decorated function."""

  __modgud_eop_form__: Final[EopFormEnum] = EopFormEnum.COND

  def __call__(self, *clauses: eop_clause[T], default: D) -> T | D:
    """Return the value of the first clause whose test is true, else ``default``.
    As in Elixir, a test is true unless it is ``None`` or ``False``, so ``0`` and ``[]`` are true.
    Tests run in order and only the selected value is evaluated.
    """
    self._refuse()

  @staticmethod
  @Invert(bootstrap='modgud', keys={'port': EopFormEnum.COND})
  def _refuse(*, port: EopPort) -> NoReturn:
    """Delegate the refusal of an un-rewritten call to the injected adapter."""
    port.refuse()


eop_cond: Final[EopCond] = EopCond()
