"""
Domain ports (interfaces) for modgud.

Port definitions (interfaces) used throughout the modgud library
following domain-driven design principles. Ports are preferred over
ABC base classes for better flexibility and duck typing support.

This module re-exports port definitions from their individual files
following the single class per file principle.
"""

from .decorator_factory_port import (
  ChainableDecoratorFactoryPort,
  SafeDecoratorFactoryPort,
)
from .di_port import (
  DependencyResolverPort,
  DIContainerPort,
  InjectableDetectorPort,
  InjectionMapBuilderPort,
)
from .guard_port import GuardRuntimePort, GuardValidatorPort, GuardWrapperPort
from .maybe_port import MaybePort
from .pipeable_port import PipeableFactoryPort, PipeablePort
from .result_port import ResultPort
from .shape_port import ShapePort
from .transform_port import (
  ASTTransformationPort,
  ImplicitReturnTransformerPort,
  SourceExtractorPort,
  TransformationResultPort,
)

__all__ = [
  'ASTTransformationPort',
  'ChainableDecoratorFactoryPort',
  'DependencyResolverPort',
  'DIContainerPort',
  'GuardRuntimePort',
  'GuardValidatorPort',
  'GuardWrapperPort',
  'ImplicitReturnTransformerPort',
  'InjectableDetectorPort',
  'InjectionMapBuilderPort',
  'MaybePort',
  'PipeablePort',
  'PipeableFactoryPort',
  'ResultPort',
  'SafeDecoratorFactoryPort',
  'ShapePort',
  'SourceExtractorPort',
  'TransformationResultPort',
]
