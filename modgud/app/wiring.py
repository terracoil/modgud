"""Composition root: discover modgud's ports and adapters once, on first use."""

from idunn import Idunn, ReportMap


class Wiring:
  """Idunn bootstrap for the modgud package, called from the decorators' ``__new__``."""

  ROOT_PACKAGE: str = 'modgud'

  @classmethod
  def ensure(cls) -> ReportMap:
    """Run discovery for ``modgud`` once per process; later calls return the cached report."""
    return Idunn().bootstrap(cls.ROOT_PACKAGE)
