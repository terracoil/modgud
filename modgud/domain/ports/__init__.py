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
from .maybe_port import MaybePort
from .pipeable_port import PipeableFactoryPort, PipeablePort
from .result_port import ResultPort

__all__ = [
  'ChainableDecoratorFactoryPort',
  'MaybePort',
  'PipeablePort',
  'PipeableFactoryPort',
  'ResultPort',
  'SafeDecoratorFactoryPort',
]