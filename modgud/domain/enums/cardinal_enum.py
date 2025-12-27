"""
Cardinal enum for modgud domain layer.

Enumeration for cardinal directions: N, S, E, W;
"""

from enum import Enum, IntEnum, auto

__all__ = ['Cardinal']


class Cardinal(IntEnum):
  """Strategy for handling guard failures."""
  NORTH=0
  SOUTH=1
