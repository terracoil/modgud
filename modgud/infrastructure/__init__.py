"""Core infrastructure for modgud - foundational functionality for expression-oriented features.

This package provides the core building blocks that support the expression-oriented
functionality but aren't part of the primary user-facing API.
"""

from .chainable_expression import ChainableExpression
from .chained_expression_factory import ChainedExpressionFactory
from .common_guards import CommonGuards
from .di.energy_inverter import EnergyInverter
from .di.interface_discovery import InterfaceDiscovery
from .di.registration_strategies import RegistrationStrategies
from .di.service_container import ServiceContainer
from .err_result import ErrResult
from .guard_registry import GuardRegistry
from .guard_runtime import GuardRuntime
from .maybe_factory import MaybeFactory
from .nothing_maybe import Nothing
from .ok_result import Ok
from .pipeable_factory import PipeableFactory
from .pipeable_wrapper import Pipeable
from .result_factory import ResultFactory
from .safe_expression_factory import SafeExpressionFactory
from .service_locator import ServiceLocator
from .some_maybe import Some
from .transform import ImplicitReturnTransformer

__all__ = [
  'ChainableExpression',
  'ChainedExpressionFactory',
  'CommonGuards',
  'EnergyInverter',
  'ErrResult',
  'GuardRegistry',
  'GuardRuntime',
  'ImplicitReturnTransformer',
  'InterfaceDiscovery',
  'MaybeFactory',
  'Nothing',
  'Ok',
  'PipeableFactory',
  'Pipeable',
  'RegistrationStrategies',
  'ResultFactory',
  'SafeExpressionFactory',
  'ServiceContainer',
  'ServiceLocator',
  'Some',
]
