"""Modgud bootstrap: autodiscovery of ports/adapters."""

# from idunn import Idunn


class Modgud:
  """Bootstrap entry point that wires ports to adapters."""

  def __init__(self) -> None:
    """Run port/adapter autodiscovery."""
    print('Running autodiscovery of ports/adapters...')
    # Idunn().autodiscover('modgud')   # idempotent; survives a prior reset()
