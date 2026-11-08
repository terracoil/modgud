"""``eop_case``: Elixir's ``case`` as an expression, lowered by the implicit-return rewrite."""

from __future__ import annotations

from typing import Final, NoReturn, TypeVar

from idunn import Invert

from modgud.domain.enums import EopFormEnum
from modgud.domain.ports import EopPort
from modgud.domain.types import eop_clause

T = TypeVar('T')
D = TypeVar('D')


class EopCase:
  """Typed stand-in for ``eop_case``; the rewrite replaces every call inside a decorated function."""

  __modgud_eop_form__: Final[EopFormEnum] = EopFormEnum.CASE

  def __call__(self, subject: object, *clauses: eop_clause[T], default: D) -> T | D:
    """Return the value of the first clause whose pattern matches ``subject``, else ``default``.
    The subject is evaluated once. A clause test is a pattern such as ``Point(0, eop_var.y)``,
    or ``eop_when(pattern, guard)``. Captures are visible only in that clause's guard and value.
    """
    self._refuse()

  @staticmethod
  @Invert(bootstrap='modgud', keys={'port': EopFormEnum.CASE})
  def _refuse(*, port: EopPort) -> NoReturn:
    """Delegate the refusal of an un-rewritten call to the injected adapter."""
    port.refuse()


eop_case: Final[EopCase] = EopCase()
