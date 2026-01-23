"""Domain protocols for modgud.

Protocol definitions (interfaces) used throughout the modgud library
following domain-driven design principles. Protocols are preferred over
ABC base classes for better flexibility and duck typing support.

This module re-exports port definitions from the ports package.
"""

from .ports import (
  ChainableDecoratorFactoryPort,
  MaybePort,
  PipeableFactoryPort,
  PipeablePort,
  ResultPort,
  SafeDecoratorFactoryPort,
)

__all__ = [
  'ChainableDecoratorFactoryPort',
  'MaybePort',
  'PipeablePort',
  'PipeableFactoryPort',
  'ResultPort',
  'SafeDecoratorFactoryPort',
]
