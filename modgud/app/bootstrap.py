"""Bootstrap configuration for dependency injection."""

from gleipnyr import (
  DependencyResolverService,
  DIContainerAdapter,
  EnergyInverter,
  InjectableDetectorService,
  ServiceLocator,
)

from modgud.infrastructure.guard import GuardRuntimeAdapter, GuardWrapperService
from modgud.infrastructure.transform import ImplicitReturnAdapter


def configure_dependencies() -> ServiceLocator:
  """Configure all dependencies for the application.

  This function sets up the service locator with all necessary
  infrastructure implementations.

  :return: Configured service locator
  """
  locator = ServiceLocator.instance()

  # Clear any existing registrations
  locator.clear()

  # Register guard-related services
  locator.register_factory(GuardRuntimeAdapter, lambda: GuardRuntimeAdapter())

  locator.register_factory(
    GuardWrapperService,
    lambda: GuardWrapperService(locator.resolve(GuardRuntimeAdapter)),
  )

  # Register transformation services
  locator.register_factory(ImplicitReturnAdapter, lambda: ImplicitReturnAdapter())

  # Register DI services
  locator.register_factory(
    DIContainerAdapter,
    lambda: DIContainerAdapter(EnergyInverter.instance()),
  )

  locator.register_factory(InjectableDetectorService, lambda: InjectableDetectorService())

  locator.register_factory(
    DependencyResolverService,
    lambda: DependencyResolverService(locator.resolve(InjectableDetectorService)),
  )

  return locator


# Auto-configure on module import
_configured = False
if not _configured:
  configure_dependencies()
  _configured = True
