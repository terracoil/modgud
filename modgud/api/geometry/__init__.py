"""
Geometry API - Mathematical and geometric utilities for modgud.

This module provides geometry-related functionality including:
- Vector operations and path manipulation
- Linear interpolation (Lerper)
- Joinery calculations for woodworking joints
"""

from .joinery import Joinery
from .lerper import Lerper, LerpStrategy
from .vector import Vector
from .vector_path import VectorPath
from .vector_protocol import VectorProtocol

__all__ = [
  'Joinery',
  'Lerper',
  'LerpStrategy',
  'Vector',
  'VectorPath',
  'VectorProtocol',
]
