"""
Dependency Injection (DI) infrastructure for modgud.

This module provides the core dependency injection infrastructure including
service container, auto-registration, and interface-based dependency resolution.
"""

from .energy_inverter import EnergyInverter
from .interface_discovery import InterfaceDiscovery
from .registration_strategies import RegistrationStrategies
from .service_container import ServiceContainer, ServiceNotFoundError

__all__ = [
  'EnergyInverter',
  'ServiceContainer',
  'ServiceNotFoundError',
  'InterfaceDiscovery',
  'RegistrationStrategies',
]
