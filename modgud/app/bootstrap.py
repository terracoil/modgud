"""Bootstrap configuration for dependency injection."""

from ..domain.ports import (
  DependencyResolverPort,
  DIContainerPort,
  GuardRuntimePort,
  GuardWrapperPort,
  ImplicitReturnTransformerPort,
  InjectableDetectorPort,
)
from ..infrastructure.di.energy_inverter import EnergyInverter
from ..infrastructure.di_adapters import (
  DependencyResolverService,
  DIContainerAdapter,
  InjectableDetectorService,
)
from ..infrastructure.guard import (
  GuardRuntimeAdapter,
  GuardWrapperService,
)
from ..infrastructure.service_locator import ServiceLocator
from ..infrastructure.transform import ImplicitReturnAdapter


def configure_dependencies() -> ServiceLocator:
  """
  Configure all dependencies for the application.

  This function sets up the service locator with all necessary
  infrastructure implementations for the ports defined in the domain.

  :return: Configured service locator
  """
  locator = ServiceLocator.instance()

  # Clear any existing registrations
  locator.clear()

  # Register guard-related services
  locator.register_factory(GuardRuntimePort, lambda: GuardRuntimeAdapter())

  locator.register_factory(
    GuardWrapperPort,
    lambda: GuardWrapperService(locator.resolve(GuardRuntimePort)),
  )

  # Register transformation services
  locator.register_factory(ImplicitReturnTransformerPort, lambda: ImplicitReturnAdapter())

  # Register DI services
  locator.register_factory(
    DIContainerPort,
    lambda: DIContainerAdapter(EnergyInverter.instance()),
  )

  locator.register_factory(InjectableDetectorPort, lambda: InjectableDetectorService())

  locator.register_factory(
    DependencyResolverPort,
    lambda: DependencyResolverService(locator.resolve(InjectableDetectorPort)),
  )

  return locator


# Auto-configure on module import
_configured = False
if not _configured:
  configure_dependencies()
  _configured = True
