"""Domain ports (interfaces) for modgud.

Port definitions (interfaces) used throughout the modgud library
following domain-driven design principles. Ports are preferred over
ABC base classes for better flexibility and duck typing support.

This module re-exports port definitions from their individual files
following the single class per file principle.
"""

# Import base ports first (no dependencies on other ports)
from .decorator_factory import (
  ChainableDecoratorFactoryPort,
  SafeDecoratorFactoryPort,
)
from .di import (
  DependencyResolverPort,
  DIContainerPort,
  InjectableDetectorPort,
  InjectionMapBuilderPort,
)
from .guard import GuardRuntimePort, GuardValidatorPort, GuardWrapperPort
from .maybe_port import MaybePort
from .noise_port import NoisePort

# Import ports with dependencies on base ports
from .pipeable import PipeableFactoryPort, PipeablePort
from .result_port import ResultPort
from .shape_port import ShapePort
from .transform import (
  ASTTransformationPort,
  ImplicitReturnTransformerPort,
  SourceExtractorPort,
  TransformationResultPort,
)
from .vector_port import VectorPort

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
  'NoisePort',
  'PipeablePort',
  'PipeableFactoryPort',
  'ResultPort',
  'SafeDecoratorFactoryPort',
  'ShapePort',
  'SourceExtractorPort',
  'TransformationResultPort',
  'VectorPort',
]
