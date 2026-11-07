"""``eop_when``: a pattern with a guard, Elixir's ``pattern when guard``."""

from __future__ import annotations

from typing import Final

from modgud.domain.enums import EopFormEnum
from modgud.domain.errors import MarkerNotRewrittenError


class EopWhen:
  """Typed stand-in for ``eop_when``; recognised only inside ``eop_case`` and ``eop_match``."""

  __modgud_eop_form__: Final[EopFormEnum] = EopFormEnum.WHEN

  def __call__(self, pattern: object, guard: object) -> object:
    """Attach ``guard`` to ``pattern``.
    As in Elixir, the guard passes only when it is exactly ``True``, and a guard that raises
    counts as no match. A mistake inside a guard therefore falls through silently.
    """
    raise MarkerNotRewrittenError(EopFormEnum.WHEN)


eop_when: Final[EopWhen] = EopWhen()
