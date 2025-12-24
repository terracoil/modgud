"""
Geometry API - Mathematical and geometric utilities for modgud.

This module provides geometry-related functionality including:
- Vector operations and path manipulation
- Linear interpolation (Lerper)
- Joinery calculations for woodworking joints
- Simplex noise generation with fractal Brownian motion
"""

from .joinery import Joinery
from .lerper import Lerper, LerpStrategy
from .simplex_noise import SimplexNoise
from .stackable_trapezoid import StackableTrapezoid
from .vector import Vector
from .vector_path import VectorPath
from .vector_protocol import VectorProtocol

__all__ = [
  'Joinery',
  'Lerper',
  'LerpStrategy',
  'SimplexNoise',
  'StackableTrapezoid',
  'Vector',
  'VectorPath',
  'VectorProtocol',
]
