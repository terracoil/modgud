"""
Domain protocols for modgud.

Protocol definitions (interfaces) used throughout the modgud library
following domain-driven design principles. Protocols are preferred over
ABC base classes for better flexibility and duck typing support.

This module re-exports port definitions from the ports package for
backward compatibility. New code should import from .ports directly.
"""

from .ports import (
  ChainableDecoratorFactoryPort,
  MaybePort,
  PipeableFactoryPort,
  PipeablePort,
  ResultPort,
  SafeDecoratorFactoryPort,
)

# Legacy aliases for backward compatibility
ChainableDecoratorFactoryProtocol = ChainableDecoratorFactoryPort
MaybeProtocol = MaybePort
PipeableProtocol = PipeablePort
PipeableFactoryProtocol = PipeableFactoryPort
ResultProtocol = ResultPort
SafeDecoratorFactoryProtocol = SafeDecoratorFactoryPort

__all__ = [
  # New port classes
  'ChainableDecoratorFactoryPort',
  'MaybePort',
  'PipeablePort',
  'PipeableFactoryPort',
  'ResultPort',
  'SafeDecoratorFactoryPort',
  # Legacy aliases (deprecated)
  'ChainableDecoratorFactoryProtocol',
  'MaybeProtocol',
  'PipeableProtocol',
  'PipeableFactoryProtocol',
  'ResultProtocol',
  'SafeDecoratorFactoryProtocol',
]
