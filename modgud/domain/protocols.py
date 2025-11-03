"""
Domain protocols for modgud.

Protocol definitions (interfaces) used throughout the modgud library
following domain-driven design principles. Protocols are preferred over
ABC base classes for better flexibility and duck typing support.

This module re-exports protocol definitions from their individual files
following the single class per file principle.
"""

from .decorator_factory_protocol import (
  ChainableDecoratorFactoryProtocol,
  SafeDecoratorFactoryProtocol,
)
from .maybe_protocol import MaybeProtocol
from .pipeable_protocol import PipeableProtocol, PipeableFactoryProtocol
from .result_protocol import ResultProtocol

__all__ = [
  'ChainableDecoratorFactoryProtocol',
  'MaybeProtocol',
  'PipeableProtocol',
  'PipeableFactoryProtocol',
  'ResultProtocol',
  'SafeDecoratorFactoryProtocol',
]
