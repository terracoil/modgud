"""``eop_var``: the capture object used inside ``eop_case`` and ``eop_match`` patterns."""

from __future__ import annotations

from typing import Any, Final

from modgud.domain.enums import EopFormEnum
from modgud.domain.errors import MarkerNotRewrittenError


class EopVar:
  """Capture namespace: ``eop_var.name`` captures into ``name`` and ``eop_var._`` matches anything."""

  __modgud_eop_form__: Final[EopFormEnum] = EopFormEnum.VAR

  def __getattr__(self, name: str) -> Any:
    """Stand for the capture called ``name``; only the rewrite gives it a meaning."""
    # Dunder lookups come from tools such as inspect and copy; keep hasattr() honest for them.
    if name.startswith('__') and name.endswith('__'):
      raise AttributeError(name)
    raise MarkerNotRewrittenError(EopFormEnum.VAR)


eop_var: Final[EopVar] = EopVar()
